use actix_web::web;

pub mod eventos;
pub mod jogadores;
pub mod partidas;
pub mod sumula;
pub mod times;

/// Registra todas as rotas da API de uma vez, para o main.rs não precisar
/// conhecer cada endpoint individualmente.
pub fn configurar(cfg: &mut web::ServiceConfig) {
    times::configurar(cfg);
    jogadores::configurar(cfg);
    partidas::configurar(cfg);
    eventos::configurar(cfg);
    sumula::configurar(cfg);
}
