# ---------------------------------------------------------------------------
# Estágio 1 — compilação
# ---------------------------------------------------------------------------
FROM rust:1.97-slim AS builder

WORKDIR /app

# Truque de cache: compila só as dependências primeiro, usando um main.rs
# vazio. Como o Docker guarda cada camada, mexer no nosso código depois não
# invalida a camada das ~150 dependências — o rebuild cai de minutos para
# segundos. Só mudar o Cargo.toml/Cargo.lock refaz esse trabalho.
COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo "fn main() {}" > src/main.rs && \
    cargo build --release && \
    rm -rf src

# Agora sim o código de verdade.
COPY .sqlx ./.sqlx
COPY src ./src

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
     /app/target/release/basketball-api /usr/local/bin/basketball-api

# Dentro do container é preciso escutar em todas as interfaces, senão o
# mapeamento de portas do Docker não alcança o processo.
ENV BIND_ADDR=0.0.0.0:3000
EXPOSE 3000

CMD ["basketball-api"]
