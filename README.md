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
| Backend / API | `backend/` | Rust (gRPC via `tonic`) |
| Frontend Web | `frontend/` | TypeScript + React |
| Banco de dados | `db/` | PostgreSQL (container Docker) |
| Orquestração | `docker/` | Docker + Docker Compose |
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
├── backend/        # API em Rust (ainda vazio — Fase 4)
├── frontend/       # Web em TypeScript + React (ainda vazio — Fase 5)
├── db/             # Schema e migrations do PostgreSQL (ainda vazio — Fase 3)
└── docker/         # Dockerfiles e docker-compose.yml (ainda vazio — Fase 2/6)
```

Arquivos pesados (vídeos, pesos de modelo, saídas de inferência) ficam fora do
Git — veja `.gitignore`.

## Status

Projeto em desenvolvimento inicial. Consulte o histórico de decisões, fases e
pendências no diário de bordo do projeto.

## Como rodar (por enquanto)

Só o serviço de IA existe até o momento. Duas formas de rodar:

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
