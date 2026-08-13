use sqlx::PgPool;

use crate::modelos::{Evento, TipoEvento};

/// Grava um evento, derivando a pontuação a partir do tipo.
///
/// Tanto a rota REST quanto o serviço gRPC chamam esta função. Se cada um
/// tivesse seu próprio INSERT, bastaria alguém mexer só num deles para os
/// dois caminhos passarem a gravar coisas diferentes — e o bug apareceria
/// como "a súmula muda dependendo de quem registrou o evento".
pub async fn inserir_evento(
    pool: &PgPool,
    partida_id: i32,
    jogador_id: i32,
    tipo: TipoEvento,
    tempo_video_ms: Option<i32>,
) -> Result<Evento, sqlx::Error> {
    let pontos = tipo.pontos();

    sqlx::query_as!(
        Evento,
        "INSERT INTO eventos (partida_id, jogador_id, tipo, pontos, tempo_video_ms)
         VALUES ($1, $2, $3, $4, $5)
         RETURNING id, partida_id, jogador_id, tipo, pontos, tempo_video_ms, criado_em",
        partida_id,
        jogador_id,
        tipo.como_texto(),
        pontos,
        tempo_video_ms
    )
    .fetch_one(pool)
    .await
}
