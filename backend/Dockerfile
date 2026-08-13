# O contexto de build deste Dockerfile é a RAIZ do repositório, não backend/.
# Motivo: o build.rs precisa ler proto/placar.proto, que fica fora de
# backend/ de propósito (é um contrato compartilhado com o serviço de IA).
# Ver o serviço `backend` no docker-compose.yml.

# ---------------------------------------------------------------------------
# Estágio 1 — compilação
# ---------------------------------------------------------------------------
FROM rust:1.97-slim AS builder

# protoc é exigido pelo tonic-prost-build para gerar o código do gRPC.
RUN apt-get update && apt-get install -y --no-install-recommends \
        protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

# Truque de cache: compila só as dependências primeiro, com um main.rs vazio.
# Como o Docker guarda cada camada, mexer no nosso código depois não invalida
# a camada das dependências — o rebuild cai de minutos para segundos. Só
# alterar Cargo.toml/Cargo.lock refaz esse trabalho.
COPY backend/Cargo.toml backend/Cargo.lock ./
RUN mkdir src && echo "fn main() {}" > src/main.rs && \
    cargo build --release && \
    rm -rf src

# Agora o código de verdade. O proto vai para /app/proto, que é onde o
# build.rs o procura (../proto a partir de /app/backend).
COPY proto /app/proto
COPY backend/build.rs ./
COPY backend/.sqlx ./.sqlx
COPY backend/src ./src

# As macros do sqlx normalmente consultam o banco durante a compilação para
# validar o SQL — mas aqui não existe banco algum. SQLX_OFFLINE manda usar o
# cache de queries em .sqlx/, gerado por `cargo sqlx prepare`.
ENV SQLX_OFFLINE=true

# O touch garante que o cargo enxergue o main.rs real como mais novo que o
# dummy do passo de cache; sem isso ele poderia pular a recompilação.
RUN touch src/main.rs && cargo build --release

# ---------------------------------------------------------------------------
# Estágio 2 — runtime
# ---------------------------------------------------------------------------
# Imagem final só com o binário: sem compilador, sem código-fonte, sem cargo.
# Além de muito menor, reduz a superfície de ataque (Fase 7).
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Usuário sem privilégios. Se um dia alguém explorar a aplicação, não cai
# como root dentro do container. (Mesma lição da Fase 2, onde o container
# rodando como root gerava arquivos que o usuário não conseguia apagar.)
RUN useradd --create-home --uid 10001 api
USER api

COPY --from=builder --chown=api:api \
     /app/backend/target/release/basketball-api /usr/local/bin/basketball-api

# Dentro do container é preciso escutar em todas as interfaces, senão o
# mapeamento de portas do Docker não alcança o processo.
ENV BIND_ADDR=0.0.0.0:3000
ENV GRPC_ADDR=0.0.0.0:50051
EXPOSE 3000 50051

CMD ["basketball-api"]
