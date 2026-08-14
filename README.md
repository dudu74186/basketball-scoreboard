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
| Backend / API | `backend/` | Rust + actix-web, `sqlx` para o banco, `tonic` para gRPC |
| Frontend Web | `frontend/` | TypeScript + React (Vite) |
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
├── proto/          # Contrato gRPC compartilhado entre a IA e o backend
├── ia/             # Serviço de visão computacional (Python + YOLO)
│   ├── main.py
│   ├── cliente_placar.py  # Cliente gRPC que reporta eventos à API
│   ├── gerado/     # Stubs gerados do .proto (via ./gerar_stubs.sh)
│   ├── models/     # Pesos de modelo (ex.: yolo11n.pt) — não versionado
│   ├── samples/    # Vídeos de teste locais — não versionado
│   └── outputs/    # Resultados de inferência (runs/, vídeos gerados) — não versionado
├── backend/        # API em Rust + actix-web
│   ├── src/main.rs
│   └── Cargo.toml  # Cargo.lock é versionado (é uma aplicação, não lib)
├── frontend/       # Painel de operação (Vite + React + TypeScript)
│   └── src/
│       ├── api.ts        # Cliente da API + tipos espelhando o backend
│       └── componentes/  # PainelCadastro, PainelPartidas, PainelPlacar
├── db/             # Schema e migrations do PostgreSQL
│   ├── migrations/ # Arquivos .sql numerados (compatíveis com sqlx-cli)
│   └── README.md
├── docker/         # (reservado para configs de orquestração — vazio por enquanto)
└── docker-compose.yml  # Orquestração dos serviços (banco + API)
```

Arquivos pesados (vídeos, pesos de modelo, saídas de inferência) ficam fora do
Git — veja `.gitignore`.

## Status

Projeto em desenvolvimento inicial. Consulte o histórico de decisões, fases e
pendências no diário de bordo do projeto.

## Como rodar (por enquanto)

### Stack completa (banco + API)

```bash
cp .env.example .env   # e troque a senha
docker compose up -d
curl localhost:3000/health
```

Sobe o PostgreSQL e a API juntos. A API só inicia depois que o banco fica
saudável (`depends_on: condition: service_healthy`).

Schema e decisões de modelagem documentados em `db/README.md`.

### Backend / API

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

#### Rodando o backend localmente (sem Docker)

Requer o toolchain do Rust ([rustup](https://rustup.rs)).

```bash
cd backend/
cp .env.example .env   # ajuste DATABASE_URL com as credenciais do .env da raiz
cargo run
```

⚠️ As macros do `sqlx` validam o SQL **em tempo de compilação**, então
`cargo build` precisa do banco no ar (`docker compose up -d db`). Se alterar
alguma query, rode `cargo sqlx prepare` para atualizar o cache em
`backend/.sqlx/` — é ele que permite compilar sem banco dentro do Docker.

### Frontend — painel de operação

Requer a stack no ar (passo acima).

```bash
cd frontend/
npm install
cp .env.example .env
npm run dev          # abre em http://localhost:5173
```

Numa tela só: cadastrar times e jogadores, criar partida, registrar
cesta/lance livre/falta com um clique e acompanhar placar e súmula. É a
ferramenta de teste da API — e será a de validação da IA, quando ela
começar a detectar eventos sozinha.

A súmula se recarrega a cada 3s, então eventos que chegarem por fora da
tela (via gRPC, vindos do serviço de IA) aparecem sozinhos.

⚠️ O backend só aceita chamadas do navegador vindas das origens listadas em
`CORS_ORIGINS` (padrão: `http://localhost:5173`). Se rodar o Vite em outra
porta, ajuste essa variável no `docker-compose.yml`.

### Comunicação IA → API (gRPC)

O serviço de visão computacional reporta as cestas detectadas via gRPC, na
porta `50051`. O contrato fica em `proto/placar.proto` — fora de `backend/`
e de `ia/` de propósito, porque é o acordo entre os dois.

| RPC | Tipo | Uso |
|---|---|---|
| `RegistrarEvento` | unário | Um evento, com confirmação |
| `RegistrarEventos` | client streaming | Fluxo de eventos por uma única conexão, com resumo ao final |

O lado Rust regenera o código a cada `cargo build` (via `build.rs`). O lado
Python precisa de `./ia/gerar_stubs.sh` quando o `.proto` mudar.

```python
from ia.cliente_placar import ClientePlacar

with ClientePlacar() as c:
    c.registrar(partida_id=1, jogador_id=1, tipo="cesta_3", tempo_video_ms=42000)
```

Assim como no REST, **a pontuação não é enviada pelo cliente** — o servidor
a deriva do tipo do evento, usando o mesmo código (`repositorio.rs`) que a
rota REST usa.

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
