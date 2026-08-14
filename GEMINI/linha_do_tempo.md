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

**4c — Containerizar e integrar (✅ concluída em 13/08/2026):**
- `sqlx-cli` instalado; `cargo sqlx prepare` gera `backend/.sqlx/` (11
  queries em cache, **versionado**). Com `SQLX_OFFLINE=true`, as macros do
  sqlx validam pelo cache em vez de consultar o banco — é o que viabiliza
  compilar dentro do Docker, onde não há banco.
- `backend/Dockerfile` multi-stage: imagem final **145 MB** contra 1,27 GB
  da imagem de compilação. Runtime sem compilador, sem código-fonte, sem
  cargo. Camada de cache de dependências separada do código.
- Roda como **usuário não-root** (uid 10001), confirmado com `id` dentro do
  container.
- **Contexto de build é a raiz do repo**, não `backend/` — o `build.rs`
  precisa de `proto/placar.proto`. Por isso existe um `.dockerignore` na
  raiz excluindo `**/target/`, mídia da IA, `.git/` etc.
- Serviço `backend` no `docker-compose.yml`, com
  `depends_on: db: condition: service_healthy` (não basta "iniciado": a API
  falharia ao abrir o pool se subisse antes do banco ficar pronto).
- **gRPC implementado** (decisão do usuário, mantida após a IA levantar que
  REST bastaria para o volume real de ~100 eventos/partida; o usuário
  preferiu gRPC por ser objetivo de aprendizado do projeto):
  - `proto/placar.proto` na raiz — contrato compartilhado, não pertence a
    nenhum dos dois serviços.
  - Rust: `tonic` 0.14 + `tonic-prost-build` no `build.rs` (regenera o
    código a cada `cargo build`; o gerado não é versionado). Servidor sobe
    em **thread própria com runtime tokio próprio**, porque misturar com o
    runtime do actix-web causa problemas sutis.
  - Dois RPCs: `RegistrarEvento` (unário) e `RegistrarEventos` (client
    streaming — uma conexão HTTP/2 para todo o fluxo de detecções).
  - Python: `ia/cliente_placar.py` + stubs em `ia/gerado/` (versionados,
    para o build da imagem de IA não precisar de protoc). Regeneração via
    `ia/gerar_stubs.sh`, que também corrige o import absoluto que o protoc
    gera e que quebraria o import como pacote.
- **`repositorio.rs` criado** para REST e gRPC compartilharem a gravação do
  evento e a regra de pontuação. Sem isso, os dois caminhos poderiam
  divergir e o bug apareceria como "a súmula muda dependendo de quem
  registrou o evento".
- Erros de banco traduzidos para status gRPC (`INVALID_ARGUMENT`,
  `ALREADY_EXISTS`, `INTERNAL`), sem vazar detalhe do banco — mesma
  política do lado REST.
- Testado de ponta a ponta com a stack containerizada: cliente Python
  enviou 6 detecções por streaming, e a súmula lida via REST bateu
  exatamente (Eduardo 5 pts + 1 falta, Marcos 6 pts). Erros também
  testados: jogador inexistente e `tipo` não informado, ambos rejeitados.

### Fase 5 — Frontend Web
✅ **Concluída em 14/08/2026** (funcionando em modo dev; containerizar o
frontend fica para a Fase 6).

**O que foi feito:**
- `actix-cors` adicionado ao backend — era a pendência que bloqueava tudo.
  Origens vêm de `CORS_ORIGINS` (padrão `http://localhost:5173`),
  **listadas explicitamente**, nunca `*`: liberar qualquer origem deixaria
  qualquer site fazer chamadas à API pelo navegador de quem estivesse
  logado. Testado que origem não autorizada recebe 400.
- Projeto Vite + React + TS em `frontend/`, com:
  - `src/api.ts` — cliente e tipos espelhando `backend/src/modelos.rs`.
  - `src/componentes/` — `PainelCadastro`, `PainelPartidas`, `PainelPlacar`.
  - `src/index.css` — tokens de cor com suporte a tema claro/escuro.
- A súmula recarrega a cada 3s, para eventos que chegarem por gRPC (do
  serviço de IA) aparecerem sozinhos na tela. WebSocket seria mais elegante
  — anotado como melhoria possível, não necessária para um painel de
  operação.
- Detalhe que travou o build: o template novo do Vite liga
  `erasableSyntaxOnly`, que **proíbe propriedades declaradas no construtor**
  (`constructor(public status: number)`). Resolvido declarando o campo
  separadamente.
- Validação feita: `tsc -b && vite build` limpo; teste de fumaça via SSR
  (`renderToString`) confirmando que a árvore de componentes renderiza sem
  erro; CORS testado nas duas direções; contratos da API conferidos contra
  os tipos do frontend.
  ⚠️ **A interface não foi aberta num navegador de verdade** — não havia
  ferramenta de browser nesta sessão. O usuário precisa confirmar
  visualmente.

**Decisões tomadas pelo usuário em 13/08/2026:**
- Ferramenta: **Vite + React + TypeScript** (SPA). Escolhido em vez de
  Next.js porque o backend já é o Rust — recursos de servidor do Next não
  seriam usados.
- Escopo da primeira interface: **painel de teste/operação**, não só
  visualização. Numa tela: cadastrar times/jogadores, criar partida,
  botões para registrar cesta/falta, e a súmula atualizando ao lado.
- **Motivo de vir antes da IA:** essa tela vira a ferramenta de validação
  da própria IA. Quando o YOLO começar a detectar, será preciso ver o que
  ele detectou, corrigir erros e confirmar eventos — a interface de
  operação já é isso. Construir a IA antes significaria depurá-la no
  terminal lendo JSON.

~~⚠️ Pendência: backend sem CORS~~ — resolvida em 14/08/2026.

### Fase 6 — Orquestração via Docker Compose
✅ **Concluída em 14/08/2026** para banco + backend + frontend.
(O serviço de IA continua fora do compose de propósito — ver nota no fim.)

- `frontend/Dockerfile` multi-stage: `node:22-alpine` builda os estáticos,
  `nginxinc/nginx-unprivileged:1.27-alpine` serve. **75 MB** finais, sem
  Node nem código-fonte na imagem, rodando como **uid 101 (não-root)**.
- `npm ci` (não `install`) no build: instala exatamente o que está no
  `package-lock.json`, tornando o build reproduzível.
- **`frontend/nginx.conf` faz duas coisas importantes:**
  1. **Fallback de SPA** (`try_files ... /index.html`) — sem isso,
     recarregar a página numa rota interna do React daria 404.
  2. **Proxy de `/api/` para `http://backend:3000/`** (a barra final é o
     que remove o prefixo: `/api/times` chega como `/times`).
- **Por que o proxy, e não chamar `localhost:3000` direto:** o Vite injeta
  as variáveis `VITE_*` em **tempo de build**, não de execução. Cravar
  `http://localhost:3000` na imagem faria o painel funcionar só na própria
  máquina — quebraria acessado do PC Windows ou do celular. Com o proxy, o
  navegador chama o próprio domínio (`/api`), e **não há CORS envolvido**
  por ser mesma origem. `VITE_API_URL` entra como `ARG` do Dockerfile,
  com padrão `/api`.
- Validado de ponta a ponta:
  - Os 3 containers sobem juntos com `docker compose up -d`.
  - Bundle contém `` `/api` `` e **zero** ocorrências de `localhost:3000`.
  - Fluxo completo (criar time/jogador, erro 404) funcionando pelo proxy.
  - SPA fallback: rota inexistente devolve 200 com o index.
  - `id` no container confirma uid 101.
  - **Teste decisivo:** acesso por `http://192.168.3.63:8080` (IP da rede)
    funciona. Já a API direta em `:3000`, chamada com `Origin` desse IP,
    responde 200 mas **sem** `access-control-allow-origin` — ou seja, o
    navegador descartaria a resposta. É exatamente o problema que o proxy
    evita.
- ⏳ Paridade Linux/Windows: o compose está pronto para isso, mas **não foi
  testado no Windows** ainda.

**Nota — por que a IA não está no compose:** o serviço de `ia/` é um job de
processamento em lote (roda, processa um vídeo, termina), não um servidor
que fica no ar. Além disso, exige `--gpus all` e volumes de mídia pesada.
Colocá-lo no compose como serviço de longa duração não faria sentido hoje.
Reavaliar quando a IA virar um consumidor contínuo de stream da câmera.

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
- Consolidar documentação do projeto (arquitetura final, decisões tomadas, licença).

---

## 🎯 Fase de IA — plano de ordenação (definido em 13/08/2026)

> O usuário declarou a intenção de treinar o YOLO para detectar "marcações,
> jogadores, números, cestas". Análise feita no chat e registrada aqui para
> não se perder. **Nada disso foi iniciado ainda.**

**Reenquadramento importante:** "treinar o YOLO" não é uma tarefa, são
~5 problemas distintos, com dificuldades muito diferentes. Tentar resolver
todos de uma vez é o erro clássico. Ordem recomendada, priorizando o que
fecha um ciclo funcionando mais cedo:

| # | Etapa | Racional | Dificuldade |
|---|---|---|---|
| a | **Bola + aro** (2 classes) | Bola cruzando o aro de cima para baixo = cesta. Já dá **placar automático** mesmo sem saber quem fez. Menor modelo, maior retorno. | Média |
| b | **Rastreamento de jogadores** | O YOLO **já detecta "person" de fábrica** (confirmado no teste da Fase 2). Falta só tracking — o ultralytics tem ByteTrack/BoT-SORT embutido. "Quem estava com a bola no arremesso" atribui a cesta. | Baixa |
| c | **2 ou 3 pontos** | **Não usar YOLO aqui.** Linha de quadra se resolve melhor com homografia (mapear a quadra para um plano 2D); a posição do arremessador decide. Mais robusto que treinar detecção de linha. | Média |
| d | **Números de camisa (OCR)** | Deixar por **último** — de longe o mais difícil (número pequeno, borrado, girado, tapado, jogador de costas). Contorno viável: o operador associa "jogador rastreado nº3 = Eduardo" uma vez por partida, pela interface da Fase 5. | Alta |

**(a) + (b) já entregam uma súmula automática funcionando** — só depois
disso vale investir nas partes difíceis.

**Dois pontos práticos levantados:**
1. **O gargalo real é o dataset, não o treino.** Anotar bola/aro em
   milhares de frames à mão é inviável. Procurar dataset público de
   basquete (Roboflow Universe tem vários com bola/aro/jogador anotados)
   e complementar com os vídeos do usuário.
2. **A GTX 1650 tem 4 GB de VRAM.** Dá para treinar `yolo11n` e talvez
   `yolo11s` em 640px com batch pequeno; modelos `m`/`l`/`x` não cabem.
   Isso reforça a estratégia de poucas classes por modelo.

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
