use actix_web::{get, post, web, HttpResponse};
use sqlx::PgPool;

use crate::erro::ApiError;
use crate::modelos::{Evento, NovoEvento};

#[get("/partidas/{id}/eventos")]
async fn listar(pool: web::Data<PgPool>, id: web::Path<i32>) -> Result<HttpResponse, ApiError> {
    let eventos = sqlx::query_as!(
        Evento,
        "SELECT id, partida_id, jogador_id, tipo, pontos, tempo_video_ms, criado_em
           FROM eventos
          WHERE partida_id = $1
          ORDER BY tempo_video_ms NULLS LAST, id",
        id.into_inner()
    )
    .fetch_all(pool.get_ref())
    .await?;

    Ok(HttpResponse::Ok().json(eventos))
}

/// Registra um evento numa partida. É por aqui que o serviço de IA vai
/// reportar as cestas detectadas (via a API, na entrega 4c).
#[post("/partidas/{id}/eventos")]
async fn criar(
    pool: web::Data<PgPool>,
    id: web::Path<i32>,
    corpo: web::Json<NovoEvento>,
) -> Result<HttpResponse, ApiError> {
    let partida_id = id.into_inner();

    // A pontuação vem do próprio tipo do evento — o cliente não manda
    // `pontos`. Ver TipoEvento::pontos() em modelos.rs.
    let pontos = corpo.tipo.pontos();

    let evento = sqlx::query_as!(
        Evento,
        "INSERT INTO eventos (partida_id, jogador_id, tipo, pontos, tempo_video_ms)
         VALUES ($1, $2, $3, $4, $5)
         RETURNING id, partida_id, jogador_id, tipo, pontos, tempo_video_ms, criado_em",
        partida_id,
        corpo.jogador_id,
        corpo.tipo.como_texto(),
        pontos,
        corpo.tempo_video_ms
    )
    .fetch_one(pool.get_ref())
    .await?;

    Ok(HttpResponse::Created().json(evento))
}

pub fn configurar(cfg: &mut web::ServiceConfig) {
    cfg.service(listar).service(criar);
}
