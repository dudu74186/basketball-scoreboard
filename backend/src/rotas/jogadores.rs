use actix_web::{get, post, web, HttpResponse};
use sqlx::PgPool;

use crate::erro::ApiError;
use crate::modelos::{Jogador, NovoJogador};

#[derive(serde::Deserialize)]
struct FiltroJogadores {
    time_id: Option<i32>,
}

#[get("/jogadores")]
async fn listar(
    pool: web::Data<PgPool>,
    filtro: web::Query<FiltroJogadores>,
) -> Result<HttpResponse, ApiError> {
    // Um SQL só para os dois casos (com e sem filtro): quando time_id vem
    // vazio, o primeiro lado do OR já é verdadeiro e o filtro é ignorado.
    // Evita duplicar a query só por causa de um parâmetro opcional.
    let jogadores = sqlx::query_as!(
        Jogador,
        "SELECT id, nome, numero_camisa, time_id, criado_em
           FROM jogadores
          WHERE $1::int IS NULL OR time_id = $1
          ORDER BY numero_camisa NULLS LAST, nome",
        filtro.time_id
    )
    .fetch_all(pool.get_ref())
    .await?;

    Ok(HttpResponse::Ok().json(jogadores))
}

#[post("/jogadores")]
async fn criar(
    pool: web::Data<PgPool>,
    corpo: web::Json<NovoJogador>,
) -> Result<HttpResponse, ApiError> {
    let jogador = sqlx::query_as!(
        Jogador,
        "INSERT INTO jogadores (nome, numero_camisa, time_id)
         VALUES ($1, $2, $3)
         RETURNING id, nome, numero_camisa, time_id, criado_em",
        corpo.nome,
        corpo.numero_camisa,
        corpo.time_id
    )
    .fetch_one(pool.get_ref())
    .await?;

    Ok(HttpResponse::Created().json(jogador))
}

pub fn configurar(cfg: &mut web::ServiceConfig) {
    cfg.service(listar).service(criar);
}
