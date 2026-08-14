# 📝 Registro de Sessão - Placar Automático de Basquete

Este arquivo documenta o progresso da nossa colaboração, incluindo aulas didáticas, perguntas pendentes e o status atual do projeto.

---

## 📌 ESTADO ATUAL (ler isto primeiro ao retomar) — atualizado 14/08/2026 (sessão 15)

**Onde paramos:** Fases 0, 1, 2, 3, 4, 5 e **6 concluídas**. Repositório:
**https://github.com/dudu74186/basketball-scoreboard**.

**O que já funciona de ponta a ponta:**
- Serviço de IA (`ia/`): builda e roda em Docker com GPU real (GTX 1650),
  lê modelo/vídeo/saída via variáveis de ambiente, persiste resultado no
  host via volumes. **Ainda não integrado ao pipeline** — o `main.py` só
  detecta objetos genéricos (pessoas), não cestas.
- Banco (`db/`): PostgreSQL 17, schema completo, view `vw_sumula`.
- Backend (`backend/`): Rust + actix-web + sqlx, **11 endpoints REST** e
  **servidor gRPC** (porta 50051) com 2 RPCs. Containerizado (imagem de
  145 MB, usuário não-root).
- **A stack inteira sobe com `docker compose up -d`** (banco + API juntos,
  com a API esperando o banco ficar saudável).
- Cliente gRPC em Python (`ia/cliente_placar.py`) testado contra o backend
  containerizado: eventos enviados por streaming aparecem corretamente na
  súmula lida via REST.
- **Frontend (`frontend/`)**: painel de operação em Vite + React + TS.
  Cadastra times/jogadores, cria partida, registra eventos por clique e
  mostra placar + súmula (recarregada a cada 3s, para pegar eventos vindos
  por gRPC).
- **`docker compose up -d` sobe os 3 serviços.** Painel em
  **http://localhost:8080**, com o nginx servindo os estáticos e fazendo
  proxy de `/api` para o backend — funciona igual acessado pelo IP da rede
  (testado em `192.168.3.63:8080`), sem CORS por ser mesma origem.
  Para desenvolver com hot reload, `npm run dev` em `frontend/` continua
  valendo (aí sim usa CORS, origem `localhost:5173`).

⚠️ **Ao mexer no backend:** `cargo build` exige o banco no ar (macros do
sqlx validam SQL em tempo de compilação). Se alterar alguma query, rode
`cargo sqlx prepare` para atualizar `backend/.sqlx/`, senão o build do
Docker quebra.

Comandos de execução completos estão no `README.md` da raiz.

**Estrutura de pastas atual:**
```
.
├── docs/        (planejamento — Ferramentas.md, Regras IA.md, Placar automático, canvas)
├── GEMINI/      (esta pasta — memória do assistente)
├── ia/          (Python + YOLO — main.py, Dockerfile, requirements.txt, .env.example,
│                 models/, samples/, outputs/ — os 3 últimos locais, fora do Git)
├── db/          (PostgreSQL — migrations/*.sql numeradas + README.md)
├── proto/       (placar.proto — contrato gRPC compartilhado IA <-> backend)
├── backend/     (Rust — src/{main,erro,modelos,repositorio,grpc}.rs + rotas/,
│                 build.rs, Dockerfile, .sqlx/ versionado; target/ gitignored)
├── frontend/    (Vite+React+TS — src/api.ts, src/componentes/, Dockerfile,
│                 nginx.conf; node_modules/ e dist/ gitignored)
├── docker/      (reservado, ainda vazio)
├── docker-compose.yml  (orquestra db + backend + frontend; a IA fica fora,
│                       por ser job em lote com GPU — ver nota na Fase 6)
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

**Próximo passo — combinado com o usuário:** iniciar a **fase de IA**, com
**dataset híbrido** (escolha explícita dele em 14/08/2026): começar de um
dataset público de basquete (Roboflow Universe tem vários com bola/aro/
jogador anotados), treinar, ver onde o modelo erra nos vídeos reais dele, e
só então anotar os casos difíceis — em vez de anotar às cegas.

Ordem da fase de IA (detalhada no fim de [[linha_do_tempo]]):
bola+aro → tracking de jogadores → 2x3 pontos por homografia → OCR de
camisa por último.

Primeiros passos concretos quando retomar:
1. Escolher/baixar o dataset público de bola+aro.
2. Montar `data.yaml` e script de treino em `ia/` (`yolo11n`, 640px, batch
   pequeno — limite dos 4 GB da GTX 1650).
3. Avaliar no vídeo real `COMETAS X CESB` (que não estará no treino).
4. Lógica de cesta (bola cruzando o aro de cima para baixo) — não é IA, é
   lógica temporal, e costuma ser subestimada (falso positivo com rebote,
   bola passando na frente do aro, tabela).
5. Ligar no gRPC: hoje o `main.py` só salva vídeo anotado, precisa passar a
   chamar o `ClientePlacar` ao detectar cesta.

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

---

## 🔁 Sessão 11 (12/08/2026 — sessão Claude Code): Fase 4b — API REST completa

**O que aconteceu:** implementados os 11 endpoints da API, com o código
organizado em módulos em vez de tudo no `main.rs`:

```
backend/src/
├── main.rs      (bootstrap: env, pool, servidor, JsonConfig)
├── erro.rs      (ApiError + traducao de SQLSTATE para status HTTP)
├── modelos.rs   (structs das tabelas + TipoEvento)
└── rotas/
    ├── mod.rs, times.rs, jogadores.rs, partidas.rs, eventos.rs, sumula.rs
```

**Decisões de design que valem lembrar:**

1. **Pontuação derivada no servidor.** O cliente manda só `tipo`
   (`cesta_2`/`cesta_3`/`lance_livre`/`falta`); `TipoEvento::pontos()`
   decide o valor. Testado: mandar `"pontos": 50` no corpo é simplesmente
   ignorado, grava 2. Se o cliente mandasse a pontuação, nada impediria
   registrar cesta de 2 valendo 50.
2. **`TipoEvento` é enum, não String.** Valor inválido morre na
   desserialização (400), sem nem chegar ao banco. O CHECK da migration
   continua como última linha de defesa.
3. **Erros de banco traduzidos por SQLSTATE** em `erro.rs`: `23505`→409
   (unique), `23503`→400 (FK), `23514`→400 (check). Erro inesperado: log
   completo no servidor, cliente recebe só `{"erro":"erro interno"}` —
   não vazar detalhe de banco é item de OWASP (Fase 7).
4. **Súmula é só leitura** (`GET /partidas/{id}/sumula`), lendo `vw_sumula`.
   Não existe endpoint para "atualizar súmula" — ela é sempre derivada dos
   eventos, coerente com a decisão da Fase 3.
5. Na súmula foi preciso usar `AS "coluna!"` nas macros do sqlx: ele não
   consegue inferir que colunas de view com SUM/COUNT não são nulas.

**Dois defeitos encontrados nos próprios testes e corrigidos:**
- Concordância: `"partida não encontrado"` (vinha de concatenar
  `"{nome} não encontrado"`). `ApiError::NaoEncontrado` passou a carregar a
  frase pronta.
- JSON malformado devolvia **texto puro**, enquanto o resto da API devolve
  `{"erro": ...}`. Um cliente que sempre faz `response.json()` quebraria só
  no caminho de erro. Corrigido com `web::JsonConfig::error_handler` +
  nova variante `ApiError::RequisicaoInvalida`.

**Testado de ponta a ponta contra o banco real:**
- Fluxo feliz: criar 2 times → 2 jogadores → 1 partida → 5 eventos →
  súmula com os totais conferindo (7 e 1 pontos, 1 falta).
- Caminhos de erro: 409 (camisa duplicada), 400 (FK inexistente), 400
  (time contra si mesmo), 400 (modalidade `7x7`), 404 (partida e súmula
  inexistentes), 400 (tipo inválido, JSON malformado, campo faltando).
- Dados de teste removidos com TRUNCATE ao final; banco ficou limpo.

**⚠️ Ponto de atenção para a 4c:** as macros do sqlx exigem o banco no ar
durante o `cargo build`. O build dentro do Docker **não terá** banco, então
antes da 4c é preciso instalar `sqlx-cli` e rodar `cargo sqlx prepare`, que
gera o diretório `.sqlx/` (versionado) com o cache das queries, permitindo
compilar em modo offline. Vale explicar isso ao usuário quando chegar lá.

**Status:** entregas 4a e 4b concluídas. Falta a 4c.

**Próximos Passos na Retomada:**
1. `cargo sqlx prepare` (instalar `sqlx-cli` antes) para viabilizar build
   offline.
2. `Dockerfile` multi-stage do backend (builder + runtime enxuto) e
   adicionar o serviço `backend` ao `docker-compose.yml` (`BIND_ADDR` deve
   virar `0.0.0.0:3000` no container, e `DATABASE_URL` apontar para `db`).
3. gRPC via `tonic` para o serviço de IA reportar eventos à API.
4. Lembrar: `source "$HOME/.cargo/env"` antes de usar cargo em comandos
   não-interativos.

---

## 🔁 Sessão 12 (13/08/2026 — sessão Claude Code): Fase 4c — containerização e gRPC

**O que aconteceu:** fechada a Fase 4 com a containerização do backend e a
comunicação IA ↔ API via gRPC.

### Parte 1 — Containerização

1. `sqlx-cli` instalado; `cargo sqlx prepare` gerou `backend/.sqlx/` com 11
   queries em cache. **Versionado de propósito** — com `SQLX_OFFLINE=true`,
   é o que permite compilar sem banco dentro do Docker.
2. `backend/Dockerfile` multi-stage: **145 MB** finais contra 1,27 GB da
   imagem `rust:1.97-slim` usada para compilar. Camada de dependências
   separada do código (mexer no src não recompila as ~150 dependências).
3. Roda como **não-root** (uid 10001) — confirmado com `id` no container.
4. Serviço `backend` no compose, com `depends_on: condition:
   service_healthy`.
5. Validado: stack completa sobe junta, os 11 endpoints respondem pelo
   container, e os dados sobrevivem a restart do backend e do banco.

### Parte 2 — gRPC (decisão do usuário)

**Contexto da decisão:** a IA levantou honestamente que, para o volume real
de tráfego IA→API (~100 eventos por partida, uma cesta a cada ~30s), o
endpoint REST `POST /partidas/{id}/eventos` já resolveria, e que gRPC
adicionaria complexidade (codegen em duas linguagens, segunda porta,
schemas sincronizados) sem ganho prático — o link onde performance importa
é câmera→IA, que não passa por aí. **O usuário optou por gRPC mesmo assim**,
por ser objetivo declarado de aprendizado do projeto. Decisão respeitada.

6. `proto/placar.proto` criado **na raiz do repo** — é contrato entre os
   dois serviços, não pertence a nenhum deles.
7. Rust: `tonic` 0.14 + `tonic-prost-build`. Atenção: no tonic 0.14 o
   codegen prost saiu para crates separados (`tonic-prost`,
   `tonic-prost-build`) — `tonic_build::compile_protos` sozinho não basta.
8. **O servidor gRPC roda em thread própria com runtime tokio próprio.**
   O actix-web usa um runtime com características diferentes; misturar os
   dois no mesmo executor causa problemas sutis. Duas threads, dois
   runtimes.
9. Dois RPCs: `RegistrarEvento` (unário) e `RegistrarEventos` (client
   streaming — uma conexão HTTP/2 para todo o fluxo de detecções).
10. **`repositorio.rs` extraído**: REST e gRPC chamam a MESMA função para
    gravar evento e derivar pontuação. Sem isso, os dois caminhos poderiam
    divergir e o sintoma seria "a súmula muda dependendo de quem registrou".
11. Python: `ia/cliente_placar.py` (com context manager) + stubs em
    `ia/gerado/`, **versionados** para o build da imagem de IA não precisar
    de protoc. `ia/gerar_stubs.sh` regenera e corrige o import absoluto que
    o protoc gera (`import placar_pb2`), que quebraria o import como pacote.

### Detalhes técnicos que custaram tempo (para não repetir)

- O prost **encurta nomes de enum**: `TIPO_EVENTO_NAO_ESPECIFICADO` no
  .proto vira `TipoEvento::NaoEspecificado` no Rust (remove o prefixo
  repetido do nome do enum). Primeiro build falhou por isso.
- O **contexto de build do Docker teve que virar a raiz do repo**, porque
  o `build.rs` lê `../proto/placar.proto`. Exigiu criar `.dockerignore` na
  raiz (excluindo `**/target/`, mídia da IA, `.git/`) e ajustar todos os
  `COPY` do Dockerfile para caminhos a partir da raiz.
- `protobuf-compiler` precisou ser instalado **dentro** da imagem builder.

### Testes feitos (todos passaram)

- RPC unário: `cesta_3` → 3 pontos.
- Streaming: 6 detecções numa conexão → 11 pontos, resumo correto.
- Erros: jogador inexistente → `INVALID_ARGUMENT`; `tipo` não informado →
  `INVALID_ARGUMENT` (importante: no proto3 campo não preenchido chega como
  zero, e rejeitar explicitamente evita virar "cesta de 2" silenciosa).
- **Teste cruzado:** eventos gravados via gRPC aparecem corretos na súmula
  lida via REST — prova que os dois caminhos convergem no mesmo lugar.
- Tudo repetido contra a stack **containerizada**, não só local.
- Dados de teste limpos com TRUNCATE ao final.

**Status:** Fase 4 concluída inteira (4a + 4b + 4c).

**Próximos Passos na Retomada:**
1. **Fase 5 — Frontend Web** (TypeScript + React) consumindo a API REST.
   Perguntar ao usuário qual ferramenta de build/framework (Vite? Next?) —
   regra de ouro: não escolher sozinho.
2. **Alternativa que talvez valha mais:** voltar ao serviço de IA e fazer
   a detecção de cestas de verdade. Hoje o `main.py` roda o `yolo11n.pt`
   genérico, que só detecta "person"/"sports ball" — não sabe o que é uma
   cesta, nem quem fez. Sem isso, o pipeline IA→gRPC→banco→súmula está
   pronto mas nunca recebe dado real. Vale colocar essa escolha para o
   usuário.
3. Lembrar: `source "$HOME/.cargo/env"` antes de cargo em comandos não
   interativos; `cargo sqlx prepare` após mudar queries.

---

## 🔁 Sessão 13 (13/08/2026 — sessão Claude Code): decisões da Fase 5 e plano da fase de IA

**Nada foi implementado nesta entrada** — o usuário pediu a recomendação de
ordem, tomou as decisões, e pausou antes de começar o código do frontend.

**Pergunta do usuário:** quer uma interface para facilitar os testes e
depois treinar o YOLO para detectar "marcações, jogadores, números,
cestas" — e perguntou qual ordem de criação seria recomendada.

**Recomendação dada (e aceita): interface primeiro.** O argumento decisivo
não foi "é mais fácil", e sim que **a interface vira a ferramenta de
validação da própria IA**: quando o YOLO começar a detectar, será preciso
ver o que ele detectou, corrigir e confirmar eventos. Fazendo a IA antes,
a depuração seria no terminal lendo JSON.

**Decisões do usuário para a Fase 5:**
- **Vite + React + TypeScript** (em vez de Next.js — o backend já é o Rust,
  os recursos de servidor do Next não seriam usados).
- Escopo: **painel de teste/operação** (cadastro de times/jogadores, criar
  partida, botões de cesta/falta, súmula ao lado) — e não apenas uma tela
  de visualização, justamente para substituir o `curl` nos testes.

**Plano da fase de IA registrado em [[linha_do_tempo]]** (seção própria no
fim do arquivo). Pontos centrais do que foi analisado:
- "Treinar o YOLO" foi reenquadrado como ~5 problemas distintos, não um.
- Ordem recomendada: (a) bola+aro → (b) tracking de jogadores → (c) 2x3
  pontos por **homografia, não YOLO** → (d) OCR de camisa por último.
- (a)+(b) já entregam súmula automática funcionando.
- O YOLO já detecta "person" de fábrica; falta só tracking (ByteTrack já
  vem no ultralytics).
- **O gargalo real é o dataset, não o treino** — sugerido partir de dataset
  público (Roboflow Universe) em vez de anotar do zero.
- **VRAM de 4 GB (GTX 1650)** limita a `yolo11n`/`yolo11s` em 640px com
  batch pequeno.

**Pendência técnica prevista (importante):** o backend **não tem CORS
configurado**. É a primeira coisa a resolver quando a Fase 5 começar —
adicionar `actix-cors`, senão o navegador bloqueia toda chamada do Vite
para a API e o frontend não funciona.

**Estado do repositório:** inalterado em relação à Sessão 12, exceto por
esta documentação. `frontend/` continua só com `.gitkeep`.

**Próximos Passos na Retomada:**
1. `actix-cors` no backend (bloqueia tudo do frontend).
2. `npm create vite@latest frontend -- --template react-ts` e construir o
   painel de operação.
3. Dockerizar o frontend e adicionar ao `docker-compose.yml` (Fase 6).
4. Só então a fase de IA, na ordem registrada em [[linha_do_tempo]].

---

## 🔁 Sessão 14 (14/08/2026 — sessão Claude Code): Fase 5 — painel de operação

**O que aconteceu:**

1. **CORS resolvido primeiro** (era a pendência que bloqueava tudo, prevista
   na Sessão 13). `actix-cors` adicionado, com as origens vindas de
   `CORS_ORIGINS` e **listadas explicitamente** — nunca `*`. Liberar
   qualquer origem permitiria que qualquer site na internet chamasse a API
   pelo navegador de quem estivesse logado. Testado nos dois sentidos:
   `localhost:5173` recebe `access-control-allow-origin`; origem
   desconhecida leva **400**.
2. Projeto Vite + React + TS criado em `frontend/`, com:
   - `src/api.ts` — cliente e tipos espelhando `backend/src/modelos.rs`.
     Note que `registrarEvento` **não envia `pontos`**, coerente com a regra
     do servidor.
   - `src/componentes/PainelCadastro.tsx` (times + jogadores),
     `PainelPartidas.tsx` (criar/abrir partida),
     `PainelPlacar.tsx` (botões +2/+3/+1/Falta por jogador, placar e súmula).
   - `src/index.css` — tokens de cor com tema claro/escuro automático.
3. **A súmula recarrega a cada 3s.** Motivo: eventos que chegarem por fora
   da tela — exatamente o caso do serviço de IA gravando via gRPC —
   aparecem sozinhos. WebSocket seria mais elegante; para um painel de
   operação, o polling resolve sem complexidade extra. Anotado como
   melhoria futura possível, não necessária.
4. O placar de cada time é **somado a partir da súmula**, não guardado —
   mesma disciplina do backend e do banco.

**Detalhe que travou o build:** o template atual do Vite liga
`erasableSyntaxOnly` no TypeScript, que **proíbe propriedades declaradas no
construtor** (`constructor(public status: number)`). Corrigido declarando o
campo separadamente na classe `ApiError`.

**Correções de documentação feitas de passagem:** o `README.md` ainda dizia
que o gRPC viria "mais adiante" (já está pronto), que o compose orquestrava
"só o banco" (já tem a API), e tinha uma seção duplicada de como rodar o
backend. Os três corrigidos.

**Validação feita:**
- `tsc -b && vite build` limpo.
- **Teste de fumaça via SSR**: `renderToString` da árvore de componentes,
  confirmando que tudo renderiza sem estourar (o `tsc` pega erro de tipo,
  não erro de execução). Todos os cartões apareceram no HTML.
- Módulos servidos pelo dev server sem 404.
- Contratos da API conferidos contra os tipos do frontend.

⚠️ **Limite importante desta validação:** a interface **não foi aberta num
navegador de verdade** — não havia ferramenta de browser nesta sessão. O
usuário precisa confirmar visualmente. Se algo estiver errado, será layout
ou interação, não build nem contrato de API (esses estão verificados).

**Dados de teste:** foram deixados no banco de propósito (2 times, 2
jogadores, 1 partida), para o usuário abrir a tela e já ver conteúdo.
Limpar com:
`docker compose exec db psql -U basquete -d placar_basquete -c "TRUNCATE eventos, partidas, jogadores, times RESTART IDENTITY CASCADE;"`

**Status:** Fase 5 concluída em modo dev. Containerizar o frontend fica
para a Fase 6.

**Próximos Passos na Retomada:**
1. Perguntar ao usuário se a interface ficou boa visualmente.
2. **Fase 6** — containerizar o frontend (build estático + nginx) e colocar
   os 3 serviços no `docker-compose.yml`.
3. Ou pular para a **fase de IA** (o usuário demonstrou interesse), seguindo
   o plano de ordenação no fim de [[linha_do_tempo]]: bola+aro → tracking
   → 2x3 por homografia → OCR de camisa por último.

---

## 🔁 Sessão 15 (14/08/2026 — sessão Claude Code): Fase 6 — orquestração completa

**Contexto:** usuário confirmou que o frontend ficou bom, decidiu fazer o
**dataset híbrido** na fase de IA, mas pediu para fazer a Fase 6 antes.

**O que foi feito:**

1. `frontend/Dockerfile` multi-stage — `node:22-alpine` builda,
   `nginxinc/nginx-unprivileged:1.27-alpine` serve. **75 MB** finais,
   **uid 101 (não-root)**, sem Node nem código-fonte na imagem final.
   `npm ci` em vez de `install`, para build reproduzível a partir do lock.
2. `frontend/nginx.conf` com fallback de SPA e proxy `/api/` →
   `http://backend:3000/`.
3. `frontend/.dockerignore` (node_modules pesa centenas de MB e é
   reinstalado dentro da imagem).
4. Serviço `frontend` no `docker-compose.yml`, porta 8080.

### A decisão central desta sessão (vale entender)

**Problema:** o Vite injeta `VITE_*` em **tempo de build**, não de execução.
Cravar `VITE_API_URL=http://localhost:3000` na imagem faria o painel
funcionar só na própria máquina — quebraria acessado do PC Windows ou do
celular, que é justamente um objetivo do projeto.

**Solução:** o nginx serve os estáticos **e** faz proxy da API no mesmo
domínio. O bundle usa `/api` (relativo), então o navegador chama sempre o
próprio host de onde carregou a página. Dois ganhos:
- Funciona de qualquer máquina da rede sem reconfigurar nada.
- **CORS deixa de existir** nesse caminho (mesma origem). O `actix-cors`
  continua necessário só para o modo dev (Vite em `localhost:5173`).

`VITE_API_URL` entra como `ARG` do Dockerfile, com padrão `/api`.

### Validações feitas

- 3 containers sobem juntos com `docker compose up -d`.
- Bundle contém `` `/api` `` e **0 ocorrências** de `localhost:3000` —
  confirmado inspecionando o JS servido.
- Fluxo completo pelo proxy (criar time, criar jogador, erro 404 correto).
- SPA fallback: `/partida/1/ao-vivo` devolve 200 com o index.
- `docker compose exec frontend id` → `uid=101(nginx)`.
- **Teste decisivo:** `http://192.168.3.63:8080` (IP da rede) funciona.
  Em contraste, a API direta em `:3000` com `Origin` desse IP responde 200
  **sem** `access-control-allow-origin` — o navegador descartaria. Nuance
  importante: o servidor não bloqueia, quem bloqueia é o navegador; um
  `curl` retornando 200 não prova que funciona no browser.

### Decisão registrada: a IA não entra no compose

O serviço de `ia/` é **job em lote** (processa um vídeo e termina), não um
servidor de longa duração, e exige `--gpus all` + volumes de mídia pesada.
Colocá-lo como serviço do compose não faria sentido hoje. Reavaliar quando
a IA virar consumidora contínua de stream da câmera.

**Pendência:** paridade Linux/Windows está pronta no compose mas **não foi
testada no Windows**.

**Status:** Fase 6 concluída.

**Próximos Passos na Retomada — fase de IA, dataset híbrido:**
1. Escolher/baixar dataset público de bola+aro (Roboflow Universe).
2. `data.yaml` + script de treino em `ia/` (`yolo11n`, 640px, batch pequeno
   pelos 4 GB da GTX 1650).
3. Avaliar no `COMETAS X CESB`, que não estará no treino.
4. Lógica de cesta (trajetória cruzando o aro) — lógica temporal, não IA.
5. Ligar o `main.py` no `ClientePlacar` (gRPC).

---

## 🔁 Sessão 16 (14/08/2026 — sessão Claude Code): fase de IA iniciada — CVAT + primeiro treino

### CVAT instalado e no ar

- Clonado em **`~/ferramentas/cvat`**, FORA do repositório (é ferramenta de
  trabalho, não produto — seus ~14 serviços poluiriam o compose do projeto).
- **Conflito de porta resolvido:** o CVAT publica na 8080, mesma do frontend
  do projeto. Em vez de editar o `docker-compose.yml` deles (que seria
  desfeito no `git pull`), criado
  `~/ferramentas/cvat/docker-compose.override.yml` movendo para a **8081**.
  O `!override` na lista de `ports` é obrigatório: por padrão o Compose
  **soma** as listas, e sem ele a 8080 continuaria publicada.
- 14 containers no ar, API respondendo, e o frontend do projeto intacto na
  8080 (validado).
- ⏳ **Falta o usuário criar o superusuário** (interativo, envolve senha
  dele):
  `docker compose exec cvat_server bash -ic 'python3 ~/manage.py createsuperuser'`
- Fluxo de anotação documentado em `ia/treino/ANOTACAO.md`.

### Dataset público baixado

- `ia/.env` criado (não existia; o usuário não tinha onde pôr a chave) e
  `ia/.env.example` ganhou `ROBOFLOW_API_KEY`, que estava documentado no
  README mas não aparecia no exemplo.
- **Chave conferida:** está só no `ia/.env` (gitignored), o `.env.example`
  versionado ficou vazio, e 0 ocorrências no histórico do Git.
- **Erro meu, corrigido:** o padrão apontava para a **v1** do dataset, com
  só 499 imagens. A página do Universe mostra o total do *projeto*, não o de
  cada versão. A **v4** tem 7.486 (6.017 treino / 981 val / 488 teste).
  Documentado como listar versões antes de baixar.
- Classes: `ball`, `basket`, `person` — distribuição equilibrada
  (~4.900 / ~4.800 / ~4.000 caixas). 975 MB, gitignored.

### Primeiro treino em andamento

- **Teste de fumaça antes do treino longo** (2 épocas, 5% dos dados): serve
  para descobrir que o pipeline quebra em 1 minuto, não depois de horas.
  Passou.
- Confirmado de passagem que o bug do `ultralytics` com `project` relativo
  **ainda existe** (o smoke test caiu em `runs/outputs/treino/smoke`). O
  `treinar.py` não sofre porque já usa caminho absoluto — mesma correção
  aplicada no `main.py` na Fase 2.
- **Treino lançado** com `setsid nohup`, para sobreviver ao fechamento do
  terminal:
  - 60 épocas, batch 8, 640px, `yolo11n`
  - Log: `ia/outputs/treino/treino_bola_aro_v1.log`
  - Pesos sairão em `ia/outputs/treino/bola_aro_v1/weights/best.pt`
  - **~4 min/época** (metade do que eu estimara) → ~4h no total
  - Usa **2,16 GB** dos 4 GB da GTX 1650 — caberia batch 16, mas não vale
    reiniciar; anotado para o próximo treino.

**Próximos Passos na Retomada:**
1. Conferir se o treino terminou: `tail` no log e ver se `best.pt` existe.
2. **Avaliar no vídeo real** — `PESOS=... python avaliar.py`. É o passo que
   diz o que anotar: o `aro` deveria aparecer em quase todo frame (é fixo na
   quadra); se não aparecer, o modelo não generalizou para a câmera do
   usuário.
3. Anotar os casos difíceis no CVAT e retreinar com os dois datasets
   juntos (⚠️ nomes e ORDEM das classes precisam bater — os labels YOLO
   guardam o índice, não o nome).
4. Depois: lógica de cesta (bola cruzando o aro), e ligar o `main.py` ao
   `ClientePlacar` (gRPC) — essa alteração no `main.py` **exige autorização
   explícita** do usuário.
