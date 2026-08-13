use actix_web::{get, post, web, HttpResponse};
use sqlx::PgPool;

use crate::erro::ApiError;
use crate::modelos::{NovaPartida, Partida};

#[get("/partidas")]
async fn listar(pool: web::Data<PgPool>) -> Result<HttpResponse, ApiError> {
    let partidas = sqlx::query_as!(
        Partida,
        "SELECT id, modalidade, time_casa_id, time_visitante_id, data_hora, status, criado_em
           FROM partidas
          ORDER BY data_hora DESC"
    )
    .fetch_all(pool.get_ref())
    .await?;

    Ok(HttpResponse::Ok().json(partidas))
}

#[get("/partidas/{id}")]
async fn buscar(pool: web::Data<PgPool>, id: web::Path<i32>) -> Result<HttpResponse, ApiError> {
    let partida = sqlx::query_as!(
        Partida,
        "SELECT id, modalidade, time_casa_id, time_visitante_id, data_hora, status, criado_em
           FROM partidas WHERE id = $1",
        id.into_inner()
    )
    .fetch_optional(pool.get_ref())
    .await?
    // fetch_optional devolve None quando não achou; traduzimos para 404 em
    // vez de deixar virar um erro genérico de banco.
    .ok_or(ApiError::NaoEncontrado("partida não encontrada"))?;

    Ok(HttpResponse::Ok().json(partida))
}

#[post("/partidas")]
async fn criar(
    pool: web::Data<PgPool>,
    corpo: web::Json<NovaPartida>,
) -> Result<HttpResponse, ApiError> {
    // modalidade e "time contra si mesmo" são validados pelos CHECKs da
    // migration; o erro.rs traduz essa violação em 400.
    let partida = sqlx::query_as!(
        Partida,
        "INSERT INTO partidas (modalidade, time_casa_id, time_visitante_id)
         VALUES ($1, $2, $3)
         RETURNING id, modalidade, time_casa_id, time_visitante_id, data_hora, status, criado_em",
        corpo.modalidade,
        corpo.time_casa_id,
        corpo.time_visitante_id
    )
    .fetch_one(pool.get_ref())
    .await?;

    Ok(HttpResponse::Created().json(partida))
}

pub fn configurar(cfg: &mut web::ServiceConfig) {
    cfg.service(listar).service(buscar).service(criar);
}
