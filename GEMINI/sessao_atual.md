# 📝 Registro de Sessão - Placar Automático de Basquete

Este arquivo documenta o progresso da nossa colaboração, incluindo aulas didáticas, perguntas pendentes e o status atual do projeto.

---

## 📌 ESTADO ATUAL (ler isto primeiro ao retomar) — atualizado 12/08/2026

**Onde paramos:** Fases 0, 1, 2 e 3 concluídas; **Fase 4 em andamento**
(entrega 4a concluída, faltam 4b e 4c — ver [[linha_do_tempo]]).
Repositório: **https://github.com/dudu74186/basketball-scoreboard**.

**O que já funciona de ponta a ponta:**
- Serviço de IA (`ia/`): builda e roda em Docker com GPU real (GTX 1650),
  lê modelo/vídeo/saída via variáveis de ambiente, persiste resultado no
  host via volumes.
- Banco de dados (`db/` + `docker-compose.yml`): PostgreSQL 17 sobe via
  `docker compose up -d db`, schema completo aplicado (times, jogadores,
  partidas, eventos, view `vw_sumula`), testado com dados de exemplo e com
  as CHECK constraints rejeitando dado inválido.
- Backend (`backend/`): Rust 1.97.1 + actix-web + sqlx. `cargo run` sobe a
  API em `127.0.0.1:3000` com `GET /health` validando a conexão com o
  Postgres (200 quando ok, 503 quando o banco está fora — testado nos dois
  cenários). Precisa de `backend/.env` (já existe local, gitignored).

Comandos de execução completos estão no `README.md` da raiz.

**Estrutura de pastas atual:**
```
.
├── docs/        (planejamento — Ferramentas.md, Regras IA.md, Placar automático, canvas)
├── GEMINI/      (esta pasta — memória do assistente)
├── ia/          (Python + YOLO — main.py, Dockerfile, requirements.txt, .env.example,
│                 models/, samples/, outputs/ — os 3 últimos locais, fora do Git)
├── db/          (PostgreSQL — migrations/*.sql numeradas + README.md)
├── backend/     (Rust + actix-web — src/main.rs, Cargo.toml, Cargo.lock versionado,
│                 .env.example; target/ é local e gitignored)
├── frontend/    (TS+React — só .gitkeep, Fase 5 ainda não começou)
├── docker/      (reservado, ainda vazio)
├── docker-compose.yml  (orquestra só o serviço `db` por enquanto)
├── .env.example (POSTGRES_USER/PASSWORD/DB) — .env real já existe local, gitignored
├── .gitignore, README.md
```

**Pendências reais em aberto (nenhuma bloqueia o próximo passo):**
1. Limpeza cosmética: `ia/outputs/runs/detect/predict-2` e `predict-3` são
   resíduos de teste com dono `root` — usuário ainda não rodou o
   `sudo rm -rf` (pendente desde a Sessão 8). Não afeta nada, só sujeira
   local.
2. A pasta `runs/` de **7,4GB** na raiz de `Documentos/Python/` (fora deste
   repositório) continua sem limpar — só mexer com pedido explícito.
3. Licença do repositório: ainda não escolhida.
4. Estratégia de branches (proteção de `main`): ainda não configurada, todo
   commit até agora foi direto em `main`.
5. ~~`rustup`/toolchain do Rust~~ — instalado em 12/08/2026 (Rust 1.97.1,
   via script oficial, em `~/.cargo`). Nota para sessões futuras: o
   `.bashrc` do Arch tem `[[ $- != *i* ]] && return` no topo, então em
   comandos não-interativos é preciso `source "$HOME/.cargo/env"` antes de
   usar `cargo`/`rustc`.
6. O container `basketball-db` pode estar rodando neste momento (subido
   durante o teste da Fase 3, via `docker compose up -d db`) — verificar com
   `docker ps` ao retomar; não há problema em deixar rodando ou parar com
   `docker compose down`.
7. **Dívida de segurança aceita conscientemente:** o banco está publicado em
   `0.0.0.0:5432` (alcançável pela rede local). Usuário optou por manter
   assim para acessar do PC Windows. Registrado na Fase 7 de
   [[linha_do_tempo]] para ser revisitado. **Não "corrigir" por conta
   própria** — foi decisão explícita dele.

**Próximo passo:** entrega **4b** da Fase 4 — endpoints REST de `times`,
`jogadores`, `partidas`, `eventos` e consulta da súmula (lendo `vw_sumula`),
usando as macros do `sqlx` que validam SQL em tempo de compilação. Depois,
4c (Dockerfile do backend + gRPC/tonic com o serviço de IA).

**Regras de operação que continuam valendo** (detalhes em [[autorizacoes]] e
[[funcoes]]): só editar diretamente dentro de `GEMINI/`; nunca editar `.py`
ou `.md`/canvas fora da `GEMINI/` sem autorização explícita *a cada pedido*;
nunca escolher/aplicar linguagem ou ferramenta sozinho, só sugerir; postura
de mentor didático (usuário é programador júnior).

---

## 🎓 Aulas Didáticas

### Aula 1: O Pipeline de Visão Computacional
**Conceito:** O projeto funciona como uma linha de montagem:
1.  **Captura:** Recebimento dos frames (fotos) do vídeo via OpenCV.
2.  **Detecção (YOLOv11):** Identificação de objetos (bola, aro, jogadores) em cada frame usando a GPU NVIDIA.
3.  **Lógica (Rastreamento):** Algoritmo que monitora a trajetória da bola para identificar cestas.
4.  **Exibição:** Persistência no SQLite e interface web via Django.

### Aula 2: Preparando o Terreno com Conda
**Conceito:** Uso de ambientes virtuais para isolar dependências e evitar conflitos de versões, especialmente ao lidar com bibliotecas complexas como PyTorch e CUDA.
- **Ambiente:** `placar_basquete` (Python 3.10).
- **Aceleração:** Uso de `torch.cuda` para processamento paralelo na GPU.

---

## ❓ Perguntas Pendentes

1.  **Instalação:** Conseguiu criar o ambiente Conda e instalar as bibliotecas (torch, ultralytics, opencv, flask) sem erros?
2.  **Teste de GPU:** Qual foi a saída do comando de verificação do CUDA?
    ```python
    python -c "import torch; print('CUDA disponível:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0))"
    ```
3.  **Câmera IP:** Você já tem o endereço IP gerado pelo aplicativo no celular para testarmos a conexão?

---

## 🏀 Contexto Atual (Visão Gemini)

**Status:** Sessão encerrada em 21/05/2026. Ambiente de desenvolvimento planejado e documentado.

**Objetivo Pendente:** Validar a instalação do PyTorch com CUDA e testar a conexão com a câmera IP do celular.

**Próximos Passos na Retomada:**
1.  **Executar Teste de GPU:** Rodar o script de verificação de CUDA no ambiente Conda.
2.  **Script `main.py`:** Implementar o loop básico de captura de vídeo com OpenCV.
3.  **Primeiro Teste YOLO:** Carregar o modelo `yolo11n.pt` para detecção inicial.

---

## 🔁 Aula/Sessão 3 (11/08/2026): Pivô de escopo — estudo completo de engenharia

**Mudança decidida pelo usuário:** o projeto deixa de ser só um script de detecção e
passa a ser um estudo completo de engenharia de software e segurança, com:
- Multilinguagem (não só Python).
- Frontend web desacoplado do backend/API.
- Banco de dados dedicado (não SQLite).
- Versionamento e backup via GitHub.
- Ambiente containerizado com Docker (necessário pois o usuário programa em Linux
  e Windows e quer paridade entre os dois).
- Meta futura: app Android consumindo a mesma API.
- **Regra de ouro reforçada:** a IA nunca escolhe/aplica linguagem sozinha — só
  sugere opções, a decisão final é sempre do usuário.

Detalhes completos e o passo a passo das fases estão em [[linha_do_tempo]]. O
levantamento do que já está/falta instalar na máquina está em
[[requisitos_ambiente]] (Docker é a prioridade nº 1, ainda não instalado).

**Decisões de stack fechadas nesta sessão (11/08/2026):**
- Backend/API: **Rust** (escolhido após análise específica do requisito de streaming
  de vídeo em tempo real + comunicação de alta performance com o YOLO; comunicação
  planejada via gRPC/`tonic`).
- Frontend Web: **TypeScript + React**.
- Banco de dados: **PostgreSQL** (container Docker dedicado).
- App Android (futuro): **Kotlin nativo**.
- Detalhes e justificativas completas em [[sugestoes]].

**Status:** stack de linguagens fechado. Falta instalar o Docker (ainda não
instalado, ver [[requisitos_ambiente]]) e criar o repositório no GitHub.

**Próximos Passos na Retomada:**
1. Confirmar com o usuário se/quando instalar o Docker (comando já preparado em
   [[requisitos_ambiente]]).
2. Criar a estrutura de pastas do repositório (monorepo com `ia/`, `backend/`,
   `frontend/`, `docker/`) e iniciar o versionamento no GitHub (Fase 1 de
   [[linha_do_tempo]]).
3. Instalar o toolchain do Rust (`rustup`) — decidir com o usuário se local ou só
   em container.

---

## 🔁 Sessão 4 (11/08/2026, mesmo dia — sessão Claude Code): Docker instalado, faltou permissão de grupo

**O que aconteceu:** ao tentar validar o Docker (`docker run hello-world`), o
usuário bateu em `permission denied ... docker.sock`. Investigação (detalhes
completos em [[requisitos_ambiente]]) mostrou que:
- O Docker **já estava instalado** (v29.7.2) e o serviço já `active` — ou seja,
  esse passo da Fase 0 tinha avançado desde a última sessão registrada, sem
  atualização aqui.
- Faltava só o usuário `eduardo` entrar no grupo `docker`. Uma primeira tentativa
  com `sudo usermod -aG docker $USER` não gravou nada em `/etc/group` (causa não
  identificada). Repetindo com o nome literal (`sudo usermod -aG docker eduardo`),
  funcionou: `/etc/group` passou a mostrar `docker:x:962:eduardo`.

**Status ao final desta sessão:** grupo aplicado no `/etc/group`, mas a sessão de
shell do usuário ainda não tinha recarregado os grupos (isso só acontece em
logout/login novo, ou via `newgrp docker` como atalho pontual). **Ainda não
confirmado** que `docker run hello-world` funciona de fato.

**Próximos Passos na Retomada (atualizado):**
1. **Verificar primeiro:** pedir para o usuário rodar `docker run hello-world`
   (depois de já ter deslogado/logado ou usado `newgrp docker`). Se funcionar,
   Fase 0 de [[linha_do_tempo]] está com Docker resolvido — falta só GitHub.
2. Criar repositório no GitHub e estrutura de pastas do monorepo (Fase 1).
3. Instalar `nvidia-container-toolkit` quando for a Fase 2 (containerizar o
   serviço de IA com acesso à GPU).
4. Instalar o toolchain do Rust (`rustup`) — decidir com o usuário se local ou só
   em container.

---

## 🔁 Sessão 5 (11/08/2026, mesmo dia — sessão Claude Code): Docker validado com sucesso

**O que aconteceu:** o usuário rodou `docker run hello-world` e recebeu a
mensagem de sucesso completa ("Hello from Docker!", explicando os 4 passos
que o Docker executou). Isso confirma que o grupo `docker` está funcionando
corretamente e a instalação está 100% operacional.

**Status:** **Docker resolvido e validado.** Fase 0 de [[linha_do_tempo]]
está quase completa — falta apenas criar o repositório no GitHub.

**Próximos Passos na Retomada:**
1. ~~Decidir com o usuário: repositório GitHub público ou privado, e o nome do
   repositório~~ — feito, ver Sessão 6 abaixo.
2. ~~Criar a estrutura de pastas do monorepo~~ — feito, ver Sessão 6.
3. Instalar o toolchain do Rust (`rustup`) — decidir se local ou só em
   container.

---

## 🔁 Sessão 6 (11/08/2026, mesmo dia — sessão Claude Code): Fase 1 concluída — repositório GitHub criado

**O que aconteceu:**
1. Usuário decidiu: repositório **público**, nome **`basketball-scoreboard`**.
2. `gh` (GitHub CLI) não estava instalado — usuário instalou via `pacman` e
   autenticou com `gh auth login` (conta `dudu74186`).
3. Git inicializado dentro de `Projeto placar automatico de Basquete/`
   (branch `main`). Identidade de commit configurada localmente (não global):
   nome "Eduardo Vitor", e-mail noreply do GitHub — escolha do usuário para
   não expor o e-mail pessoal num repo público.
4. Descoberta importante: a pasta `runs/` na raiz de `Documentos/Python/`
   (fora do projeto) tinha **7,4GB** de frames de inferência acumulados —
   provavelmente de execuções do `main.py` rodado a partir do diretório
   errado. Não foi apagada (ação destrutiva, só sob pedido explícito), apenas
   excluída do versionamento.
5. Criado `.gitignore` cobrindo mídia (`*.mp4`, `*.pt`), `runs/`,
   `__pycache__/`, `node_modules/`, `/target/`, `.obsidian/`, segredos.
6. Criada a estrutura do monorepo: `ia/`, `backend/`, `frontend/`, `db/`,
   `docker/`.
7. **`main.py` movido para `ia/main.py`** (`mv`, conteúdo não alterado) —
   usuário deu autorização explícita para esta ação específica, conforme
   [[autorizacoes]] (regra de não mexer em `.py` sem pedido explícito a cada
   vez).
8. Criado `README.md` inicial na raiz do repo.
9. Commit inicial feito e repositório publicado:
   **https://github.com/dudu74186/basketball-scoreboard**

**Status:** Fase 1 de [[linha_do_tempo]] concluída (falta só decidir licença
e, mais adiante, estratégia de branches).

**Próximos Passos na Retomada:**
1. Fase 2: escrever `Dockerfile` para o serviço de IA (`ia/main.py`),
   isolando dependências (ultralytics, opencv, CUDA) sem depender do Conda
   local. Validar acesso à GPU (GTX 1650) via NVIDIA Container Toolkit.
2. Instalar o toolchain do Rust (`rustup`) — decidir se local ou só em
   container (vai ser necessário na Fase 4).
3. Considerar limpar a pasta `runs/` de 7,4GB na raiz de `Documentos/Python/`
   (fora do repo) — só com pedido explícito do usuário.

---

## 🔁 Sessão 7 (11/08/2026, mesmo dia — sessão Claude Code): Reorganização geral de pastas

**O que aconteceu:** usuário pediu para organizar toda a estrutura de pastas
do projeto seguindo boas práticas, com front e back bem separados.

1. Usuário autorizou explicitamente mover os `.md`/canvas de planejamento
   (fora da `GEMINI/`) para uma nova pasta `docs/` — conteúdo não alterado,
   só localização (`git mv` detectado como rename puro).
   - `docs/Ferramentas.md`, `docs/Regras IA.md`,
     `docs/Placar automático (IA).md`, `docs/Fluxograma Infraestrutura.canvas`.
2. Artefatos locais não versionados (mídia, pesos de modelo, saídas de
   inferência) foram organizados dentro de `ia/` em subpastas dedicadas — só
   `mv` de arquivos já cobertos pelo `.gitignore`, sem necessidade de
   autorização especial:
   - `ia/models/yolo11n.pt`
   - `ia/samples/teste.mp4`
   - `ia/outputs/output.mp4` e `ia/outputs/runs/` (antiga `runs/` da raiz do
     projeto, 53MB de frames de inferência antigos)
3. `README.md` atualizado com a árvore de pastas completa e explicação de
   cada diretório.
4. `GEMINI/` não foi movida nem renomeada (permanece na raiz, conforme regra
   de ouro em [[autorizacoes]] — é a própria pasta citada pela regra).

**Estrutura final da raiz do projeto:**
```
.
├── docs/       (documentação/planejamento — vault Obsidian)
├── GEMINI/     (memória do assistente de IA)
├── ia/         (visão computacional — Python, com models/samples/outputs locais)
├── backend/    (API Rust — vazio, Fase 4)
├── frontend/   (Web TS+React — vazio, Fase 5)
├── db/         (PostgreSQL — vazio, Fase 3)
├── docker/     (Dockerfiles/compose — vazio, Fase 2/6)
├── .gitignore
└── README.md
```

**Nota:** a pasta `runs/` de 7,4GB na raiz de `Documentos/Python/` (fora
deste repositório) continua intocada — não faz parte desta reorganização,
só seria removida com pedido explícito do usuário.

**Status:** estrutura de pastas organizada e commitada. Front (`frontend/`) e
back (`backend/`) já estavam desacoplados desde a Fase 1; esta sessão limpou
a raiz e organizou os artefatos locais do serviço de IA.

**Próximos Passos na Retomada:** os mesmos da Sessão 6 (Fase 2 — Dockerfile
do serviço de IA; instalar `rustup`).

---

## 🔁 Sessão 8 (11/08/2026, mesmo dia — sessão Claude Code): Fase 2 concluída — serviço de IA containerizado com GPU

**O que aconteceu:**
1. Usuário instalou `nvidia-container-toolkit` e configurou o runtime
   (`nvidia-ctk runtime configure --runtime=docker` + restart do Docker).
   Validado com `docker run --gpus all nvidia/cuda:... nvidia-smi` — GTX 1650
   reconhecida dentro do container.
2. Usuário autorizou duas alterações pontuais em `ia/main.py`:
   - Tornar `SHOW_VIDEO` (janela do OpenCV) controlável por variável de
     ambiente, `False` por padrão em container (sem display).
   - Parametrizar também `MODEL_PATH`, `VIDEO_SOURCE` e `OUTPUT_DIR` como
     variáveis de ambiente (documentadas em `ia/.env.example`), mantendo os
     valores antigos como padrão — decisão tomada para deixar o script
     portável entre execução local, Docker e futuramente Windows, sem
     precisar editar código de novo mais adiante.
3. Criados `ia/requirements.txt`, `ia/Dockerfile` (base
   `pytorch/pytorch:2.4.1-cuda12.1-cudnn9-runtime`) e `ia/.dockerignore`.
4. **Build testado e funcionando** (`docker build -t basketball-ia:dev .`).
   Ajuste feito no meio do caminho: `opencv-python-headless` foi removido do
   `requirements.txt` porque o `ultralytics` já traz `opencv-python`
   (com GUI) como dependência transitiva e instalava os dois, um sobrepondo
   o outro — sem efeito prático negativo, mas redundante.
5. **Execução testada com GPU real** via `docker run --gpus all` +
   volumes para `models/`, `samples/`, `outputs/`. Inferência rodou a
   ~6,7ms/frame na GTX 1650 sobre `teste.mp4` (605 frames).
6. **Dois bugs reais encontrados e corrigidos durante o teste** (não eram
   esperados, surgiram ao validar de ponta a ponta):
   - O `ultralytics` (versão 8.4.118), ao receber um `project` relativo,
     prefixa com um `runs_dir/task` interno próprio, gerando um caminho
     aninhado errado (`.../runs/detect/outputs/runs/detect/predict`) que
     ficava **fora** do volume montado — resultado se perdia ao encerrar o
     container (`--rm`). Corrigido resolvendo `OUTPUT_DIR` para caminho
     absoluto com `os.path.abspath()` antes de passar ao YOLO. Esse
     comportamento também afetaria execução local (não é bug exclusivo de
     Docker).
   - O container roda como `root` por padrão, então os arquivos de saída
     ficavam com dono `root` no host (usuário não conseguia apagar sem
     `sudo`). Corrigido documentando `--user "$(id -u):$(id -g)"` no
     comando de execução recomendado (README), sem precisar mudar a imagem.
7. `README.md` atualizado com instruções completas de execução via Docker
   (comando final, com `--gpus`, `--user`, volumes e variáveis de ambiente)
   e também localmente sem Docker.

**Status:** Fase 2 de [[linha_do_tempo]] concluída e validada
(build + execução + GPU + persistência de resultado, tudo testado).

**Próximos Passos na Retomada:**
1. Fase 3: modelar o banco de dados PostgreSQL (entidades: Partida, Time,
   Jogador, Evento, Súmula) e subir como serviço Docker próprio com volume
   persistente.
2. Instalar o toolchain do Rust (`rustup`) — necessário para a Fase 4
   (backend/API).
3. ~~Commitar os arquivos desta sessão~~ — feito, commit `526f6d0`, push
   confirmado.

**Nota de encerramento (mesma sessão):** usuário pediu para pausar aqui e
só retomar a Fase 3 quando chamar de novo. Ver seção "📌 ESTADO ATUAL" no
topo deste arquivo para o resumo rápido de retomada — foi escrita
especificamente para isso.

---

## 🔁 Sessão 9 (12/08/2026 — sessão Claude Code): Fase 3 concluída — banco PostgreSQL modelado e validado

**O que aconteceu:** usuário retomou pedindo para continuar de onde parou.
Estado foi conferido no disco (git log, resíduos `root`, `rustup`) e batia
exatamente com o que estava anotado na Sessão 8 — nenhuma surpresa.

1. Usuário decidiu a ferramenta de acesso a dados do backend Rust: **sqlx**
   (SQL puro checado em compilação) em vez de sea-orm — decisão que estava
   marcada como pendente em [[sugestoes]] desde a sessão de pivô de escopo.
2. Schema modelado e escrito em `db/migrations/*.sql` (numeração
   `0001`–`0005`, compatível com `sqlx-cli`):
   - `times`, `jogadores` (com `UNIQUE(time_id, numero_camisa)`),
     `partidas` (com `CHECK` impedindo time jogar contra si mesmo),
     `eventos` (com `CHECK` amarrando `tipo` a `pontos` — ex.: `cesta_2`
     só aceita `pontos=2`).
   - `vw_sumula`: view, não tabela — decisão deliberada para a súmula
     nunca ficar dessincronizada do que realmente está em `eventos`.
   - Justificativas completas em `db/README.md` (novo).
3. `docker-compose.yml` criado **na raiz do repositório** (primeira vez
   que aparece — antes só existia a pasta `docker/` vazia). Contém por
   enquanto só o serviço `db` (`postgres:17-alpine`, volume nomeado
   `db_data`, healthcheck `pg_isready`). Decisão de colocar o compose na
   raiz (não dentro de `docker/`) por ergonomia (`docker compose up`
   funciona direto no clone do repo, sem precisar `cd`) — mudança de
   plano em relação ao que a tabela do README dizia antes; `docker/` fica
   reservado para configs de suporte à orquestração, não o compose em si.
4. As migrations também foram montadas em `/docker-entrypoint-initdb.d`
   como atalho de bootstrap (só roda na primeira inicialização do volume)
   — deixado bem documentado em `db/README.md` que isso **não substitui**
   `sqlx migrate run`, que será o mecanismo real a partir da Fase 4.
5. `.env.example` criado na raiz; usuário copiou para `.env` (gitignored)
   com senha de desenvolvimento gerada localmente.
6. **Testado de ponta a ponta:**
   - `docker compose up -d db` → container `basketball-db` saudável.
   - As 5 migrations rodaram sem erro (confirmado nos logs do container).
   - Inserção de dados de exemplo (2 times, 2 jogadores, 1 partida, 4
     eventos) e conferência manual de `SELECT * FROM vw_sumula` — soma de
     pontos bateu exatamente com o esperado (5 e 1 pontos).
   - Duas tentativas de inserir dado inválido (`cesta_2` com 3 pontos;
     time jogando contra si mesmo) foram **corretamente rejeitadas** pelas
     `CHECK constraints` do banco.
   - Dados de teste limpos com `TRUNCATE ... RESTART IDENTITY CASCADE`
     depois da validação, deixando o schema pronto e vazio.
7. `README.md` atualizado: tabela de arquitetura, árvore de pastas e nova
   seção "Banco de dados" em "Como rodar".

**Status:** Fase 3 de [[linha_do_tempo]] concluída e validada (schema +
migrations + compose + testes de integridade, tudo testado de verdade, não
só escrito).

**Próximos Passos na Retomada:**
1. ~~Commitar e dar push nos arquivos desta sessão~~ — feito, commit `69fd400`, push confirmado.
   `db/README.md`, `docker-compose.yml`, `.env.example`, `README.md`
   atualizado) — **verificar se isso já foi feito** antes de prosseguir,
   pode ter acontecido ainda nesta mesma sessão logo em seguida.
2. Fase 4: backend/API em Rust. Precisa antes instalar `rustup` (decidir
   com o usuário se local ou só em container). Depois: `cargo init` em
   `backend/`, configurar `sqlx` apontando para o Postgres do
   `docker-compose.yml`, e `tonic`/gRPC para comunicar com `ia/`.
3. Lembrar de checar `docker ps` — o container `basketball-db` pode ter
   ficado rodando desde o teste desta sessão.

---

## 🔁 Sessão 10 (12/08/2026 — sessão Claude Code): Fase 4a — fundação do backend Rust

**O que aconteceu:**

1. **Decisões do usuário** (regra de ouro: IA não escolhe ferramenta sozinha):
   - Instalação do Rust: **script oficial rustup.rs** (entre 3 opções
     oferecidas: script, pacman, ou só em container). Sem sudo, em
     `~/.cargo`, mesmo método usado no Windows — ajuda na paridade.
   - Framework web: **actix-web**. A IA havia recomendado `axum` (mesmo
     ecossistema do `tonic`, que será usado na 4c); o usuário preferiu
     actix-web e a escolha foi respeitada sem re-discussão. Os dois
     integram com gRPC, actix só exige um pouco mais de conceito.

2. Rust 1.97.1 instalado. Adicionada a linha `. "$HOME/.cargo/env"` ao
   `~/.bashrc` (o instalador faria isso por padrão; foi rodado com
   `--no-modify-path` para não mexer no shell sem avisar).
   **Detalhe importante para sessões futuras:** o `.bashrc` do Arch começa
   com `[[ $- != *i* ]] && return`, então em comandos NÃO-interativos o
   cargo não entra no PATH — é preciso `source "$HOME/.cargo/env"` antes.

3. `cargo init` em `backend/` (crate `basketball-api`), dependências:
   actix-web 4, sqlx 0.9 (postgres/macros/chrono), serde, dotenvy,
   env_logger, log.

4. `backend/src/main.rs` escrito com:
   - Pool de conexões `sqlx` (`PgPoolOptions`, max 5) compartilhado entre
     os workers do actix via `web::Data`.
   - `GET /health` que executa `SELECT 1` **de verdade** no Postgres —
     health check que testa a dependência em vez de só devolver 200 vazio.
     Retorna **503** (não 500) quando o banco está fora: o serviço está no
     ar, a dependência é que não está.
   - `BIND_ADDR` configurável, padrão `127.0.0.1:3000` (não expõe a API na
     rede por acidente; em container vira `0.0.0.0`).

5. **Testado de verdade, incluindo o caminho de falha:**
   - `cargo build` limpo, sem warnings (53s na primeira compilação).
   - Banco no ar → `{"status":"ok","banco":"conectado"}` HTTP 200.
   - Container do banco **parado** → `{"status":"degradado",...}` HTTP 503.
   - Banco religado → HTTP 200 de novo, com o pool se recuperando sozinho
     (sem reiniciar a API).

6. **Dois bugs reais encontrados no `.gitignore`** (herdados da Fase 1,
   descobertos ao preparar o commit):
   - `/target/` estava **ancorado na raiz** do repo por causa da barra
     inicial, então NÃO cobria `backend/target/` — **1,2 GB** de artefatos
     de build teriam entrado no `git add -A`. Corrigido para `target/`.
   - `Cargo.lock` estava sendo ignorado. Para **aplicações** (binários), a
     recomendação oficial do Rust é o oposto: versionar o lock, garantindo
     que Linux, Windows, Docker e CI compilem exatamente as mesmas versões
     das ~150 dependências. Importa também para segurança (Fase 7) e CI
     (Fase 8). Removido do `.gitignore` e commitado.
   - `backend/.gitkeep` removido (a pasta já tem conteúdo real).

7. `backend/.env.example` criado; `backend/.env` real gerado localmente a
   partir das credenciais do `.env` da raiz (gitignored, confirmado).

8. `README.md` atualizado: stack do backend, árvore de pastas e seção
   "Backend / API" em "Como rodar", com a tabela de endpoints.

**Status:** entrega 4a concluída e validada. Faltam 4b (endpoints REST da
súmula) e 4c (Dockerfile do backend + gRPC com o serviço de IA).

**Próximos Passos na Retomada:**
1. Entrega **4b**: endpoints de `times`, `jogadores`, `partidas`,
   `eventos` e consulta da súmula (via `vw_sumula`), usando as macros
   `query!`/`query_as!` do sqlx (validam SQL em tempo de compilação —
   exigem o banco no ar durante o `cargo build`, ou `cargo sqlx prepare`
   para modo offline; vale explicar isso ao usuário quando chegar lá).
2. Entrega **4c**: Dockerfile multi-stage do backend, adicionar ao
   `docker-compose.yml`, e gRPC via `tonic` para a comunicação com `ia/`.
3. Lembrar: `source "$HOME/.cargo/env"` antes de usar cargo em comandos
   não-interativos.
