use actix_cors::Cors;
use actix_web::{get, http::header, web, App, HttpResponse, HttpServer, Responder};
use sqlx::postgres::PgPoolOptions;
use sqlx::PgPool;

mod erro;
mod grpc;
mod modelos;
mod repositorio;
mod rotas;

/// Resposta do /health. O `derive(Serialize)` é o que ensina o serde a
/// transformar esta struct em JSON.
#[derive(serde::Serialize)]
struct Health {
    status: &'static str,
    banco: &'static str,
}

/// Verifica se a API está de pé E se ela realmente alcança o banco.
///
/// Não basta responder "ok" — um health check que só devolve 200 sem testar
/// as dependências mente quando o banco cai. Por isso aqui roda um
/// `SELECT 1` de verdade contra o Postgres.
#[get("/health")]
async fn health(pool: web::Data<PgPool>) -> impl Responder {
    match sqlx::query_scalar::<_, i32>("SELECT 1")
        .fetch_one(pool.get_ref())
        .await
    {
        Ok(_) => HttpResponse::Ok().json(Health {
            status: "ok",
            banco: "conectado",
        }),
        Err(erro) => {
            log::error!("health check falhou ao consultar o banco: {erro}");
            // 503 (e não 500): o serviço está no ar, mas uma dependência
            // dele não está — é isso que um orquestrador precisa saber.
            HttpResponse::ServiceUnavailable().json(Health {
                status: "degradado",
                banco: "indisponivel",
            })
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Carrega o .env local (se existir). Em container, as variáveis vêm do
    // ambiente e este arquivo simplesmente não existe — por isso o .ok().
    dotenvy::dotenv().ok();
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));

    let database_url = std::env::var("DATABASE_URL")
        .expect("DATABASE_URL não definida (veja backend/.env.example)");

    // Pool de conexões: abrir uma conexão nova por request seria caro. O pool
    // mantém algumas abertas e as reaproveita entre as requisições.
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await
        .expect("falha ao conectar no Postgres");

    // 127.0.0.1 por padrão: a API não fica exposta na rede sem querer.
    // Dentro do Docker isso precisa virar 0.0.0.0, daí ser configurável.
    let bind_addr = std::env::var("BIND_ADDR").unwrap_or_else(|_| "127.0.0.1:3000".to_string());

    // O servidor gRPC sobe em paralelo, numa porta própria. É por ele que o
    // serviço de IA reporta as cestas detectadas.
    let grpc_addr = std::env::var("GRPC_ADDR").unwrap_or_else(|_| "127.0.0.1:50051".to_string());
    grpc::iniciar(pool.clone(), grpc_addr);

    // Origens autorizadas a chamar a API pelo navegador. Sem isto, o
    // frontend do Vite (porta 5173) é bloqueado pela política de mesma
    // origem. Listadas explicitamente de propósito: liberar qualquer origem
    // ("*") permitiria que qualquer site na internet fizesse chamadas à API
    // usando o navegador de quem estivesse logado.
    let origens_cors = std::env::var("CORS_ORIGINS")
        .unwrap_or_else(|_| "http://localhost:5173,http://127.0.0.1:5173".to_string());
    log::info!("origens CORS permitidas: {origens_cors}");

    log::info!("API ouvindo em http://{bind_addr}");

    HttpServer::new(move || {
        // Sem isto, um JSON malformado devolve texto puro, enquanto todo o
        // resto da API devolve {"erro": "..."}. Um cliente que sempre faz
        // response.json() quebraria justamente no caminho de erro.
        let json_cfg = web::JsonConfig::default().error_handler(|err, _req| {
            erro::ApiError::RequisicaoInvalida(err.to_string()).into()
        });

        let mut cors = Cors::default()
            .allowed_methods(vec!["GET", "POST"])
            .allowed_headers(vec![header::CONTENT_TYPE])
            .max_age(3600);
        for origem in origens_cors.split(',').map(str::trim).filter(|o| !o.is_empty()) {
            cors = cors.allowed_origin(origem);
        }

        App::new()
            .wrap(cors)
            // O pool é compartilhado entre todos os workers do actix; o
            // clone aqui é barato (é um ponteiro contado, não copia o pool).
            .app_data(web::Data::new(pool.clone()))
            .app_data(json_cfg)
            .service(health)
            .configure(rotas::configurar)
    })
    .bind(&bind_addr)?
    .run()
    .await
}
