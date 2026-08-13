# Placar Automático de Basquete

Sistema para, a partir da filmagem de um jogo de basquete (3x3 ou 5x5) pelo celular,
detectar automaticamente os pontos marcados, identificar o jogador responsável e
gerar uma súmula digital em tempo real.

Além do objetivo funcional, este repositório é usado como domínio de aplicação
prática para um estudo completo de engenharia de software: arquitetura
multi-serviço, múltiplas linguagens, containerização, banco de dados dedicado,
CI/CD e segurança aplicada.

## Arquitetura (visão geral)

| Camada | Diretório | Linguagem/Stack |
|---|---|---|
| Visão computacional / IA | `ia/` | Python + YOLOv11 (Ultralytics) |
| Backend / API | `backend/` | Rust + actix-web, `sqlx` para o banco (gRPC via `tonic` mais adiante) |
| Frontend Web | `frontend/` | TypeScript + React |
| Banco de dados | `db/` | PostgreSQL (container Docker, acesso via `sqlx` no backend) |
| Orquestração | `docker-compose.yml` | Docker + Docker Compose |
| App Android (futuro) | `mobile/` | Kotlin nativo |

Comunicação entre frontend e backend é via API (sem renderização server-side).
Todos os serviços rodam containerizados via Docker Compose, garantindo paridade
entre ambientes Linux e Windows.

## Estrutura de pastas

```
.
├── docs/           # Documentação e planejamento do projeto (vault Obsidian)
├── GEMINI/         # Contexto/memória do assistente de IA (não editar manualmente)
├── ia/             # Serviço de visão computacional (Python + YOLO)
│   ├── main.py
│   ├── models/     # Pesos de modelo (ex.: yolo11n.pt) — não versionado
│   ├── samples/    # Vídeos de teste locais — não versionado
│   └── outputs/    # Resultados de inferência (runs/, vídeos gerados) — não versionado
├── backend/        # API em Rust + actix-web
│   ├── src/main.rs
│   └── Cargo.toml  # Cargo.lock é versionado (é uma aplicação, não lib)
├── frontend/       # Web em TypeScript + React (ainda vazio — Fase 5)
├── db/             # Schema e migrations do PostgreSQL
│   ├── migrations/ # Arquivos .sql numerados (compatíveis com sqlx-cli)
│   └── README.md
├── docker/         # (reservado para configs de orquestração — vazio por enquanto)
└── docker-compose.yml  # Orquestração dos serviços (hoje só o banco)
```

Arquivos pesados (vídeos, pesos de modelo, saídas de inferência) ficam fora do
Git — veja `.gitignore`.

## Status

Projeto em desenvolvimento inicial. Consulte o histórico de decisões, fases e
pendências no diário de bordo do projeto.

## Como rodar (por enquanto)

### Banco de dados

```bash
cp .env.example .env   # e troque a senha
docker compose up -d db
docker compose exec db psql -U basquete -d placar_basquete -c '\dt'
```

Schema e decisões de modelagem documentados em `db/README.md`.

### Backend / API

Requer o banco rodando (passo acima) e o toolchain do Rust
([rustup](https://rustup.rs)).

```bash
cd backend/
cp .env.example .env   # e ajuste DATABASE_URL com as credenciais do .env da raiz
cargo run
```

Endpoints disponíveis:

| Método | Rota | O que faz |
|---|---|---|
| GET | `/health` | Responde `200` se a API alcança o banco, `503` se não |
| GET | `/times` | Lista os times |
| POST | `/times` | Cria um time — `{"nome": "..."}` |
| GET | `/jogadores?time_id=N` | Lista jogadores (o filtro é opcional) |
| POST | `/jogadores` | Cria jogador — `{"nome", "numero_camisa", "time_id"}` |
| GET | `/partidas` | Lista as partidas |
| GET | `/partidas/{id}` | Detalhe de uma partida |
| POST | `/partidas` | Cria partida — `{"modalidade", "time_casa_id", "time_visitante_id"}` |
| GET | `/partidas/{id}/eventos` | Lista os eventos da partida |
| POST | `/partidas/{id}/eventos` | Registra evento — `{"jogador_id", "tipo", "tempo_video_ms"}` |
| GET | `/partidas/{id}/sumula` | Súmula: pontos e faltas por jogador |

`tipo` aceita `cesta_2`, `cesta_3`, `lance_livre` ou `falta`. **A pontuação
não é enviada pelo cliente** — o servidor a deriva do tipo, então não há como
registrar uma cesta de 2 valendo 50.

Erros seguem sempre o mesmo formato, `{"erro": "..."}`, com o status
adequado: `400` (dado inválido), `404` (não existe), `409` (conflito, ex.:
dois jogadores com a mesma camisa no time) e `500` (erro interno, com o
detalhe apenas no log do servidor).

### Serviço de IA

Duas formas de rodar:

### Via Docker (recomendado)

Pré-requisitos: Docker + [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-container-toolkit)
(para aceleração por GPU dentro do container).

```bash
cd ia/
docker build -t basketball-ia:dev .

docker run --rm --gpus all \
  --user "$(id -u):$(id -g)" \
  -v "$(pwd)/models:/app/models:ro" \
  -v "$(pwd)/samples:/app/samples:ro" \
  -v "$(pwd)/outputs:/app/outputs" \
  basketball-ia:dev
```

- `--gpus all`: dá acesso à GPU NVIDIA dentro do container.
- `--user "$(id -u):$(id -g)"`: evita que os arquivos gerados (vídeos
  anotados) fiquem com dono `root` no seu disco.
- Os três `-v`: montam modelo, vídeo de entrada e pasta de saída como
  volumes — nada disso vai para dentro da imagem (ver `ia/.dockerignore`).
- Variáveis de ambiente disponíveis (ver `ia/.env.example`): `MODEL_PATH`,
  `VIDEO_SOURCE`, `SHOW_VIDEO`, `OUTPUT_DIR`.

Esse é o caminho pensado para funcionar igual em Linux e Windows (Fase 0),
e será substituído por um serviço orquestrado via `docker-compose.yml` na
Fase 6.

### Localmente, sem Docker

```bash
cd ia/
python main.py
```

Requer um ambiente Python com as dependências de `ia/requirements.txt`
instaladas (recomenda-se Conda; ver ambiente `placar_basquete`, Python 3.10,
com PyTorch + CUDA para aceleração por GPU). Nesse modo, `SHOW_VIDEO` é
`true` por padrão (abre a janela do OpenCV).

## Licença

A definir.
