use actix_web::{get, post, web, HttpResponse};
use sqlx::PgPool;

use crate::erro::ApiError;
use crate::modelos::{NovoTime, Time};

#[get("/times")]
async fn listar(pool: web::Data<PgPool>) -> Result<HttpResponse, ApiError> {
    // query_as! confere, em tempo de COMPILAÇÃO, que as colunas e os tipos
    // batem com a struct Time. Errar um nome de coluna aqui não compila.
    let times = sqlx::query_as!(
        Time,
        "SELECT id, nome, criado_em FROM times ORDER BY nome"
    )
    .fetch_all(pool.get_ref())
    .await?;

    Ok(HttpResponse::Ok().json(times))
}

#[post("/times")]
async fn criar(pool: web::Data<PgPool>, corpo: web::Json<NovoTime>) -> Result<HttpResponse, ApiError> {
    // $1 é um parâmetro ligado (bind), não texto concatenado na query — é
    // assim que se evita SQL injection.
    let time = sqlx::query_as!(
        Time,
        "INSERT INTO times (nome) VALUES ($1) RETURNING id, nome, criado_em",
        corpo.nome
    )
    .fetch_one(pool.get_ref())
    .await?;

    Ok(HttpResponse::Created().json(time))
}

pub fn configurar(cfg: &mut web::ServiceConfig) {
    cfg.service(listar).service(criar);
}
