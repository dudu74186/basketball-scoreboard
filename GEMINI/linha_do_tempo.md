# 🗓️ Linha do Tempo — Pivô para Estudo Completo de Engenharia de Software e Segurança

> Registrado em 11/08/2026. Este documento reflete uma mudança de escopo do usuário: o
> projeto deixou de ser "um script Python de detecção" e passou a ser um **estudo
> completo de engenharia de software, segurança e desenvolvimento web**, usando o
> placar de basquete como domínio de aplicação prática.

## Diretrizes fixadas pelo usuário (não flexibilizar sem pedido explícito)

1. **Multilinguagem:** o projeto não deve ficar só em Python. Cada camada pode ter uma
   linguagem diferente, escolhida deliberadamente para aprendizado.
2. **Front e back desacoplados:** frontend web separado do backend/API (comunicação via
   API, não templates renderizados no servidor tipo Flask+Jinja).
3. **Banco de dados dedicado:** um SGBD "de verdade" rodando como serviço próprio
   (containerizado), não SQLite em arquivo.
4. **Controle de versão:** GitHub para versionamento e backup do repositório.
5. **Docker:** ambiente de desenvolvimento containerizado — essencial porque o usuário
   programa em **dois sistemas operacionais (Linux e Windows)** e quer paridade entre
   eles.
6. **Futuro app Android:** o projeto deve prever, desde a arquitetura da API, um cliente
   mobile Android consumindo os mesmos serviços.
7. **Regra de ouro de linguagem:** a IA **nunca decide ou aplica** uma linguagem sozinha.
   Só sugere opções; a escolha final é sempre do usuário. (Ver [[requisitos_ambiente]]
   para o levantamento de ferramentas e o chat principal para as opções apresentadas.)
8. Continuam valendo as regras gerais em [[autorizacoes]] e [[funcoes]] (mentor didático,
   não editar `.py` sem autorização explícita, não editar `.md` fora de `GEMINI/`).

## Visão geral das fases

```
Fase 0  → Ambiente de máquina (Docker, Git/GitHub, editor)
Fase 1  → Repositório e versionamento (GitHub, estrutura de pastas, branches)
Fase 2  → Containerizar o serviço de IA (Python/YOLO) que já existe
Fase 3  → Banco de dados dedicado (modelagem: partidas, jogadores, eventos/pontos)
Fase 4  → Backend/API (linguagem a escolher)
Fase 5  → Frontend Web (linguagem a escolher)
Fase 6  → Orquestração completa via Docker Compose (todos os serviços juntos)
Fase 7  → Segurança aplicada (estudo prático, transversal a partir daqui)
Fase 8  → CI/CD com GitHub Actions
Fase 9  → App Android (linguagem/framework a escolher)
Fase 10 → Testes de campo real + refinamento do modelo + documentação final
```

## Detalhamento das fases

### Fase 0 — Ambiente de máquina
- Instalar **Docker** (Linux: Docker Engine + Compose via `pacman`; Windows: Docker
  Desktop + WSL2). Ver [[requisitos_ambiente]].
- Configurar Git (usuário/e-mail) e criar conta/repositório no GitHub.
- Escolher e instalar um editor único para os dois SOs (ex.: VSCode) — a definir se o
  usuário quiser.
- **Status (atualizado 11/08/2026, sessão Claude):** Docker instalado, serviço
  ativo, grupo `docker` aplicado e `docker run hello-world` confirmado com
  sucesso (ver [[sessao_atual]] e [[requisitos_ambiente]]). **Docker 100%
  resolvido.** Falta só GitHub para fechar a Fase 0.

### Fase 1 — Repositório e versionamento
- ✅ Repositório criado: **https://github.com/dudu74186/basketball-scoreboard**
  (público), em 11/08/2026.
- ✅ Estrutura de monorepo definida e criada: `ia/`, `backend/`, `frontend/`,
  `db/`, `docker/` (com `.gitkeep`; `mobile/` ainda não criado, só na Fase 9).
- ✅ `.gitignore` cobrindo mídia pesada (`*.mp4`, `*.pt`), `runs/`,
  `__pycache__/`, `node_modules/`, `/target/` (Rust), `.obsidian/`, segredos.
- ✅ README inicial na raiz.
- ✅ `ia/main.py` (movido de `main.py`, conteúdo inalterado).
- ⏳ Licença: ainda a definir.
- ⏳ Estratégia de branches (proteção de `main` + branches de feature): ainda
  não configurada — todo o trabalho até aqui foi direto em `main`.
- Identidade de commit configurada localmente (git config deste repo, não
  global): nome "Eduardo Vitor", e-mail noreply do GitHub
  (`107815999+dudu74186@users.noreply.github.com`), escolhido pelo usuário
  para manter o e-mail pessoal fora do histórico público.

### Fase 2 — Containerizar o serviço de IA existente
- ✅ **Concluída em 11/08/2026.** `nvidia-container-toolkit` instalado
  (`sudo pacman -S nvidia-container-toolkit` + `nvidia-ctk runtime configure
  --runtime=docker` + restart do serviço) — runtime `nvidia` confirmado em
  `docker info` e GPU validada dentro de um container (`nvidia-smi` via
  `docker run --gpus all`).
- ✅ `ia/Dockerfile` criado: base `pytorch/pytorch:2.4.1-cuda12.1-cudnn9-runtime`
  (já vem com PyTorch+CUDA, evita reinstalar torch CPU-only por cima),
  `ffmpeg`/`libgl1`/`libglib2.0-0` via apt para decodificação de vídeo,
  dependências Python via `ia/requirements.txt` (só `ultralytics`; não
  precisa de `opencv-python-headless` separado, o próprio `ultralytics` já
  traz `opencv-python`).
- ✅ `ia/.dockerignore` criado (deixa `models/`, `samples/`, `outputs/` fora
  da imagem — entram via volume em tempo de execução).
- ✅ `ia/main.py` alterado (autorização explícita do usuário) para ler
  `MODEL_PATH`, `VIDEO_SOURCE`, `SHOW_VIDEO`, `OUTPUT_DIR` como variáveis de
  ambiente (documentadas em `ia/.env.example`), com os valores antigos como
  padrão — script portável entre execução local, container Docker e (mais
  adiante) Windows.
- ✅ Build e execução testados de ponta a ponta com GPU real (inferência a
  ~6,7ms/frame na GTX 1650) e resultado persistido corretamente no host via
  volume montado.
- ✅ Esse serviço já funciona como "o microsserviço de visão computacional"
  standalone (roda isolado, sem depender do Conda local).
- Bugs encontrados e corrigidos durante o teste (detalhes em
  [[sessao_atual]]): (1) `ultralytics` prefixa `project` relativo com um
  `runs_dir/task` interno, gerando pasta aninhada errada — corrigido
  resolvendo `OUTPUT_DIR` para caminho absoluto (`os.path.abspath`) antes de
  passar ao YOLO; (2) container rodando como `root` gerava arquivos de saída
  com dono `root` no host — corrigido documentando `--user "$(id -u):$(id
  -g)"` no comando de execução (`docker run`), ver README.

### Fase 3 — Banco de dados dedicado
- ✅ **Concluída em 12/08/2026.**
- ✅ Ferramenta de acesso a dados/migrations decidida com o usuário:
  **sqlx** (SQL puro checado em tempo de compilação, sem ORM completo —
  escolhido por transparência pedagógica, alternativa `sea-orm` descartada
  por enquanto).
- ✅ Schema modelado em `db/migrations/` (numeração compatível com
  `sqlx-cli`): `times`, `jogadores`, `partidas`, `eventos` (tabelas) +
  `vw_sumula` (view — súmula é sempre calculada a partir de `eventos`, não
  guardada solta, para não haver dessincronização de placar). Detalhes e
  justificativas de design em `db/README.md`.
- ✅ `docker-compose.yml` criado na raiz do repo (primeira vez que o compose
  aparece — só o serviço `db` por enquanto; `ia`, `backend`, `frontend`
  entram aqui conforme forem ficando prontos, até a Fase 6). Serviço
  PostgreSQL 17 (`postgres:17-alpine`), volume nomeado `db_data`
  persistente, healthcheck via `pg_isready`.
- ✅ Bootstrap de conveniência: as migrations são montadas em
  `/docker-entrypoint-initdb.d`, rodando automaticamente na primeira
  inicialização do volume — **não é o mecanismo real de migrations**, só
  um atalho para já ter o schema em ambiente de teste antes do backend
  Rust existir. A partir da Fase 4, `sqlx migrate run` passa a ser o
  jeito certo de aplicar/versionar mudanças de schema.
- ✅ Testado de ponta a ponta: container subiu saudável, as 5 migrations
  rodaram sem erro, inserção de dados de exemplo validou a `vw_sumula`
  (soma de pontos bateu certo), e as duas `CHECK constraints` principais
  (pontos consistentes com o tipo do evento; time não pode jogar contra si
  mesmo) bloquearam dados inválidos como esperado.
- `.env.example` criado na raiz (`POSTGRES_USER/PASSWORD/DB`); `.env` real
  (gitignored) já criado localmente com senha de desenvolvimento.

### Fase 4 — Backend/API
Dividida em 3 entregas incrementais. **Entrega 4a concluída em 12/08/2026.**

**4a — Fundação (✅ concluída):**
- `rustup` instalado via script oficial rustup.rs (escolha do usuário entre
  3 opções), sem sudo, em `~/.cargo`. Rust 1.97.1. Linha
  `. "$HOME/.cargo/env"` adicionada ao `~/.bashrc`.
- Framework web escolhido pelo usuário: **actix-web** (a IA havia sugerido
  axum pela sinergia com o tonic; usuário preferiu actix-web — decisão
  respeitada, os dois integram com gRPC).
- `cargo init` em `backend/` (crate `basketball-api`), com actix-web, sqlx
  (postgres, macros, chrono), serde, dotenvy, env_logger, log.
- `backend/src/main.rs`: pool de conexões `sqlx` + endpoint `GET /health`
  que roda `SELECT 1` de verdade contra o Postgres (health check que testa
  a dependência, não só devolve 200 vazio). Retorna 503 quando o banco está
  fora — testado derrubando e religando o container.
- `BIND_ADDR` configurável, com `127.0.0.1:3000` como padrão (API não fica
  exposta na rede por acidente; em container vira `0.0.0.0`).
- **Dois bugs corrigidos no `.gitignore`** durante esta entrega, ambos
  herdados da Fase 1 (detalhes em [[sessao_atual]]): `/target/` estava
  ancorado na raiz e não pegava `backend/target/` (1,2 GB que iriam para
  o commit); e `Cargo.lock` estava sendo ignorado, quando a recomendação
  oficial do Rust é versioná-lo para aplicações.

**4b — API REST da súmula (✅ concluída em 12/08/2026):**
- Código organizado em módulos: `erro.rs`, `modelos.rs` e `rotas/`
  (um arquivo por recurso), em vez de tudo no `main.rs`.
- 11 endpoints no total (tabela completa no `README.md`): CRUD de times,
  jogadores e partidas, registro/listagem de eventos e consulta da súmula.
- Todas as queries usam as macros `query_as!`/`query_scalar!` do sqlx —
  **validadas contra o banco real em tempo de compilação**. Nome de coluna
  errado ou tipo incompatível vira erro de compilação.
  ⚠️ Consequência prática: `cargo build` **exige o banco no ar**. Para
  build sem banco (necessário no Docker da 4c), vai ser preciso
  `cargo sqlx prepare` (modo offline, gera `.sqlx/` que é versionado).
- **Pontuação derivada no servidor:** o cliente envia só o `tipo` do evento;
  `TipoEvento::pontos()` decide quantos pontos vale. Testado que enviar
  `"pontos": 50` no corpo é ignorado. A regra vive num lugar só.
- `TipoEvento` é enum, não texto livre: valor inválido é rejeitado já na
  desserialização (400), antes de chegar ao banco.
- Tratamento de erro centralizado em `erro.rs`, traduzindo códigos SQLSTATE
  do Postgres em status HTTP: `23505`→409, `23503`→400, `23514`→400,
  não-encontrado→404. Erros inesperados: detalhe só no log do servidor,
  cliente recebe `{"erro": "erro interno"}` — não vazar mensagem de banco
  na resposta é item de OWASP (Fase 7).
- Dois defeitos encontrados no próprio teste e corrigidos: concordância
  ("partida não encontrado" → "não encontrada") e erros de JSON malformado
  que saíam em texto puro em vez do formato `{"erro": ...}` padrão da API
  (corrigido com um `JsonConfig::error_handler`).
- Testado de ponta a ponta com o banco real: fluxo completo (criar times →
  jogadores → partida → eventos → súmula, com os totais conferindo) e todos
  os caminhos de erro (409, 400 de FK, 400 de CHECK, 404, JSON inválido).
  Dados de teste limpos com TRUNCATE ao final.

**4c — Containerizar e integrar (pendente):**
- `Dockerfile` multi-stage do backend + adicionar ao `docker-compose.yml`.
- Comunicação IA ↔ API via gRPC (`tonic`), conforme decidido em
  [[sugestoes]].

### Fase 5 — Frontend Web
- Linguagem/framework a escolher (opções no chat).
- Consome a API (Fase 4), exibe súmula em tempo real.

### Fase 6 — Orquestração via Docker Compose
- `docker-compose.yml` único subindo IA + backend + frontend + banco.
- Paridade Linux/Windows validada (o mesmo compose funciona nos dois SOs).

### Fase 7 — Segurança aplicada (estudo prático, transversal)
- **Dívida de segurança já identificada e aceita conscientemente pelo
  usuário (12/08/2026):** o serviço `db` do `docker-compose.yml` publica a
  porta como `"5432:5432"`, ou seja, escuta em `0.0.0.0` — o banco é
  alcançável por qualquer dispositivo da rede local (máquina está em
  `192.168.3.63`). Foi apontado durante a Fase 3 e o usuário **optou por
  manter exposto**, para poder acessar o banco a partir da outra máquina
  (Windows). Mitigação atual: a senha do `.env` é aleatória e forte.
  **Revisitar aqui:** trocar para `"127.0.0.1:5432:5432"` quando o acesso
  remoto não for mais necessário, ou substituir por uma solução melhor
  (rede Docker interna + túnel SSH, ou autenticação/TLS no Postgres).
  Cuidado extra em redes públicas (Wi-Fi de faculdade/café).
- HTTPS/TLS entre os serviços.
- Autenticação/autorização na API (ex.: JWT, OAuth — a estudar).
- Gestão de segredos (variáveis de ambiente, `.env` fora do Git, secrets do Docker).
- Scanning de dependências e de imagens Docker (ex.: `docker scan`, `trivy`).
- Checklist básico OWASP Top 10 aplicado à API e ao frontend.
- Esta fase se estende para todas as fases seguintes — segurança revisada
  continuamente, não é "feita uma vez".

### Fase 8 — CI/CD com GitHub Actions
- Pipeline de testes automatizados por linguagem.
- Build e publicação de imagens Docker.
- Deploy (alvo a definir — pode ficar só local/self-hosted no início).

### Fase 9 — App Android
- Linguagem/framework a escolher (opções no chat) — consome a mesma API da Fase 4.

### Fase 10 — Testes de campo e documentação final
- Testar com jogo real (já há vídeo de exemplo:
  `COMETAS X CESB - RODADA 16 - LCB 2021.mp4`).
- Ajustar modelo YOLO (hoje é o `yolo11n.pt` genérico, ainda não treinado para
  bola/aro/jogador).
- Consolidar documentação do projeto (arquitetura final, decisões tomadas, licença).

## Stack decidido pelo usuário (11/08/2026)

| Camada | Escolha |
|---|---|
| Visão computacional / IA | Python + YOLO (já existente, ver `main.py`) |
| Backend / API | **Rust** (comunica com o serviço de IA via gRPC/`tonic`) |
| Frontend Web | **TypeScript + React** |
| Banco de dados | **PostgreSQL** (container Docker próprio) |
| App Android (futuro, Fase 9) | **Kotlin nativo** |
| Orquestração | Docker + Docker Compose |
| Versionamento | GitHub |

Detalhes de cada decisão em [[sugestoes]].

## Pendências imediatas (bloqueando o avanço)
1. ~~Instalar Docker na máquina Linux~~ — feito e validado (`docker run
   hello-world` confirmado em 11/08/2026). Ver [[requisitos_ambiente]] e
   [[sessao_atual]].
2. ~~Decidir GitHub: repositório público ou privado, nome do repositório~~ —
   feito. Repositório público criado:
   https://github.com/dudu74186/basketball-scoreboard (Fase 1 concluída,
   exceto licença e estratégia de branches).
3. ~~Containerizar o serviço de IA (Fase 2)~~ — feito e validado com GPU real
   em 11/08/2026.
4. ~~Banco de dados PostgreSQL dedicado (Fase 3)~~ — feito e validado em
   12/08/2026 (schema, migrations, `docker-compose.yml`, testes de
   integridade).
5. Instalar toolchain do Rust (`rustup`) — a confirmar se localmente ou só
   dentro do container Docker (necessário para a Fase 4, backend/API).
6. Próximo passo natural: Fase 4 (backend/API em Rust, com `sqlx` para
   acessar o PostgreSQL e `tonic`/gRPC para comunicar com o serviço de IA).
