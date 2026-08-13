use actix_web::{http::StatusCode, HttpResponse, ResponseError};
use std::fmt;

/// Erro único da API. Todo handler devolve `Result<_, ApiError>` e o actix
/// se encarrega de transformar isso na resposta HTTP certa.
#[derive(Debug)]
pub enum ApiError {
    /// Algo deu errado ao falar com o banco.
    Banco(sqlx::Error),
    /// O recurso pedido não existe. Carrega a frase pronta ("partida não
    /// encontrada") em vez de só o nome do recurso: concatenar
    /// "{nome} não encontrado" erra a concordância em palavras femininas.
    NaoEncontrado(&'static str),
    /// O corpo da requisição não pôde ser interpretado (JSON malformado,
    /// campo faltando, valor fora do conjunto aceito).
    RequisicaoInvalida(String),
}

/// Formato padrão de erro devolvido ao cliente. Ter um formato só facilita
/// a vida de quem consome a API (frontend, app Android).
#[derive(serde::Serialize)]
struct CorpoErro {
    erro: String,
}

impl fmt::Display for ApiError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ApiError::Banco(e) => write!(f, "erro de banco: {e}"),
            ApiError::NaoEncontrado(msg) => write!(f, "{msg}"),
            ApiError::RequisicaoInvalida(msg) => write!(f, "{msg}"),
        }
    }
}

impl From<sqlx::Error> for ApiError {
    fn from(e: sqlx::Error) -> Self {
        ApiError::Banco(e)
    }
}

impl ApiError {
    /// Traduz um erro do Postgres em algo que faça sentido para o cliente.
    ///
    /// A ideia: violar uma constraint quase sempre significa que o *cliente*
    /// mandou dado inválido (culpa dele, 4xx), não que o servidor quebrou
    /// (5xx). Os códigos vêm da tabela oficial do Postgres.
    fn resposta_de_erro_de_banco(e: &sqlx::Error) -> Option<(StatusCode, String)> {
        let db_err = e.as_database_error()?;
        match db_err.code()?.as_ref() {
            // unique_violation — ex.: dois jogadores com a mesma camisa no time.
            "23505" => Some((
                StatusCode::CONFLICT,
                "já existe um registro com esses dados".to_string(),
            )),
            // foreign_key_violation — ex.: jogador apontando para time inexistente.
            "23503" => Some((
                StatusCode::BAD_REQUEST,
                "referência para um registro que não existe".to_string(),
            )),
            // check_violation — ex.: time jogando contra si mesmo.
            "23514" => Some((
                StatusCode::BAD_REQUEST,
                "os dados enviados violam uma regra do banco".to_string(),
            )),
            _ => None,
        }
    }
}

impl ResponseError for ApiError {
    fn error_response(&self) -> HttpResponse {
        match self {
            ApiError::NaoEncontrado(msg) => {
                HttpResponse::NotFound().json(CorpoErro { erro: msg.to_string() })
            }
            ApiError::RequisicaoInvalida(msg) => {
                HttpResponse::BadRequest().json(CorpoErro { erro: msg.clone() })
            }
            ApiError::Banco(e) => {
                if let Some((status, msg)) = Self::resposta_de_erro_de_banco(e) {
                    // Erro de constraint: a mensagem é genérica de propósito.
                    // Detalhe demais aqui vira mapa da estrutura do banco para
                    // quem estiver sondando a API.
                    log::warn!("requisição rejeitada pelo banco: {e}");
                    return HttpResponse::build(status).json(CorpoErro { erro: msg });
                }

                // Erro inesperado: o detalhe vai para o log do servidor, e o
                // cliente recebe só "erro interno". Vazar mensagem de erro de
                // banco na resposta é um clássico de OWASP.
                log::error!("erro inesperado de banco: {e}");
                HttpResponse::InternalServerError().json(CorpoErro {
                    erro: "erro interno".to_string(),
                })
            }
        }
    }
}
