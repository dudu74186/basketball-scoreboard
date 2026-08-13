use sqlx::PgPool;
use tonic::{Request, Response, Status, Streaming};

use crate::modelos::TipoEvento;
use crate::repositorio;

/// Código gerado pelo build.rs a partir de proto/placar.proto.
/// Não é versionado: nasce do .proto a cada compilação.
pub mod proto {
    tonic::include_proto!("placar");
}

use proto::placar_server::{Placar, PlacarServer};
use proto::{EventoDetectado, EventoRegistrado, ResumoRegistro, TipoEvento as TipoProto};

pub struct ServicoPlacar {
    pool: PgPool,
}

/// Converte o enum do protobuf para o enum do domínio.
///
/// São dois tipos separados de propósito: o do .proto é o formato do "fio"
/// (pode mudar por questões de compatibilidade entre versões), o do domínio
/// é o que as regras de negócio usam. Misturar os dois faz o protocolo
/// contaminar o resto do código.
fn converter_tipo(tipo: TipoProto) -> Result<TipoEvento, Status> {
    match tipo {
        TipoProto::Cesta2 => Ok(TipoEvento::Cesta2),
        TipoProto::Cesta3 => Ok(TipoEvento::Cesta3),
        TipoProto::LanceLivre => Ok(TipoEvento::LanceLivre),
        TipoProto::Falta => Ok(TipoEvento::Falta),
        // No proto3 todo campo tem valor padrão: um `tipo` não preenchido
        // chega aqui como zero. Rejeitar explicitamente evita que o
        // esquecimento do cliente vire, silenciosamente, uma cesta de 2.
        // (O prost encurta TIPO_EVENTO_NAO_ESPECIFICADO para NaoEspecificado,
        // removendo o prefixo repetido do nome do enum.)
        TipoProto::NaoEspecificado => {
            Err(Status::invalid_argument("tipo do evento não informado"))
        }
    }
}

/// Traduz erro de banco em status gRPC.
///
/// Mesma ideia do erro.rs no lado REST: violação de constraint é culpa do
/// dado enviado (INVALID_ARGUMENT), não falha do servidor. E o detalhe do
/// erro fica no log, não na resposta.
fn erro_para_status(erro: sqlx::Error) -> Status {
    if let Some(db) = erro.as_database_error() {
        if let Some(codigo) = db.code() {
            match codigo.as_ref() {
                "23503" => return Status::invalid_argument("partida ou jogador não existe"),
                "23514" => return Status::invalid_argument("dados violam uma regra do banco"),
                "23505" => return Status::already_exists("registro duplicado"),
                _ => {}
            }
        }
    }
    log::error!("erro inesperado de banco no gRPC: {erro}");
    Status::internal("erro interno")
}

#[tonic::async_trait]
impl Placar for ServicoPlacar {
    /// Registra um evento por vez.
    async fn registrar_evento(
        &self,
        req: Request<EventoDetectado>,
    ) -> Result<Response<EventoRegistrado>, Status> {
        let ev = req.into_inner();
        // `tipo()` é o getter gerado pelo prost: converte o i32 do fio no
        // enum, caindo no valor zero se vier algo desconhecido.
        let tipo = converter_tipo(ev.tipo())?;

        let salvo = repositorio::inserir_evento(
            &self.pool,
            ev.partida_id,
            ev.jogador_id,
            tipo,
            ev.tempo_video_ms,
        )
        .await
        .map_err(erro_para_status)?;

        Ok(Response::new(EventoRegistrado {
            id: salvo.id,
            pontos: salvo.pontos as i32,
        }))
    }

    /// Recebe um fluxo de eventos e responde uma vez, ao final.
    ///
    /// É a vantagem concreta do gRPC aqui: a IA abre UMA conexão e vai
    /// empurrando as detecções conforme processa o vídeo, sem pagar o
    /// custo de uma requisição HTTP nova a cada cesta.
    async fn registrar_eventos(
        &self,
        req: Request<Streaming<EventoDetectado>>,
    ) -> Result<Response<ResumoRegistro>, Status> {
        let mut fluxo = req.into_inner();
        let mut registrados = 0;
        let mut pontos_totais = 0;

        while let Some(ev) = fluxo.message().await? {
            let tipo = converter_tipo(ev.tipo())?;

            let salvo = repositorio::inserir_evento(
                &self.pool,
                ev.partida_id,
                ev.jogador_id,
                tipo,
                ev.tempo_video_ms,
            )
            .await
            .map_err(erro_para_status)?;

            registrados += 1;
            pontos_totais += salvo.pontos as i32;
        }

        log::info!("fluxo gRPC encerrado: {registrados} eventos, {pontos_totais} pontos");

        Ok(Response::new(ResumoRegistro {
            eventos_registrados: registrados,
            pontos_totais,
        }))
    }
}

/// Sobe o servidor gRPC. Roda numa thread própria, com seu próprio runtime
/// tokio: o actix-web usa um runtime com características diferentes, e
/// misturar os dois no mesmo executor causa problemas sutis. Duas threads,
/// dois runtimes, nenhuma disputa.
pub fn iniciar(pool: PgPool, endereco: String) {
    std::thread::spawn(move || {
        let rt = tokio::runtime::Builder::new_multi_thread()
            .enable_all()
            .build()
            .expect("falha ao criar runtime do gRPC");

        rt.block_on(async move {
            let addr = match endereco.parse() {
                Ok(a) => a,
                Err(e) => {
                    log::error!("GRPC_ADDR inválido ({endereco}): {e}");
                    return;
                }
            };

            log::info!("gRPC ouvindo em {addr}");

            let servico = ServicoPlacar { pool };
            if let Err(e) = tonic::transport::Server::builder()
                .add_service(PlacarServer::new(servico))
                .serve(addr)
                .await
            {
                log::error!("servidor gRPC encerrou com erro: {e}");
            }
        });
    });
}
