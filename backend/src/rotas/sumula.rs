use actix_web::{get, web, HttpResponse};
use sqlx::PgPool;

use crate::erro::ApiError;
use crate::modelos::LinhaSumula;

/// A súmula da partida: pontos e faltas por jogador.
///
/// Lê da view `vw_sumula`, que soma os eventos na hora da consulta — por isso
/// não existe endpoint para "atualizar a súmula". Ela é sempre um reflexo dos
/// eventos registrados, nunca um número guardado à parte.
#[get("/partidas/{id}/sumula")]
async fn consultar(pool: web::Data<PgPool>, id: web::Path<i32>) -> Result<HttpResponse, ApiError> {
    let partida_id = id.into_inner();

    // A view pode simplesmente não devolver linhas para um id inexistente —
    // o que seria indistinguível de uma partida sem jogadores. Por isso a
    // existência da partida é conferida antes, para poder responder 404.
    let existe = sqlx::query_scalar!("SELECT EXISTS(SELECT 1 FROM partidas WHERE id = $1)", partida_id)
        .fetch_one(pool.get_ref())
        .await?
        .unwrap_or(false);

    if !existe {
        return Err(ApiError::NaoEncontrado("partida não encontrada"));
    }

    // Os `as "coluna!"` dizem ao sqlx que a coluna não vem nula. Ele não
    // consegue deduzir isso sozinho em views com SUM/COUNT, mas sabemos que
    // o COALESCE da migration garante um valor.
    let linhas = sqlx::query_as!(
        LinhaSumula,
        r#"SELECT jogador_id  AS "jogador_id!",
                  jogador_nome AS "jogador_nome!",
                  time_id      AS "time_id!",
                  time_nome    AS "time_nome!",
                  pontos_totais AS "pontos_totais!",
                  faltas        AS "faltas!"
             FROM vw_sumula
            WHERE partida_id = $1
            ORDER BY pontos_totais DESC, jogador_nome"#,
        partida_id
    )
    .fetch_all(pool.get_ref())
    .await?;

    Ok(HttpResponse::Ok().json(linhas))
}

pub fn configurar(cfg: &mut web::ServiceConfig) {
    cfg.service(consultar);
}
