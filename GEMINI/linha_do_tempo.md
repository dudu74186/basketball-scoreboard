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
- Criar repositório no GitHub (público ou privado — a decidir).
- Definir estrutura de monorepo (pastas `ia/`, `backend/`, `frontend/`, `db/`,
  `mobile/`, `infra/` ou `docker/`) vs. multi-repo.
- `.gitignore` adequado a cada linguagem, README inicial, licença.
- Estratégia de branches (ex.: `main` protegida + branches de feature) — bom gancho
  para ensinar boas práticas de Git.

### Fase 2 — Containerizar o serviço de IA existente
- Escrever um `Dockerfile` para o `main.py`/YOLO atual, isolando dependências
  (ultralytics, opencv, CUDA) sem depender do Conda local.
- Validar que a GPU (GTX 1650) é acessível dentro do container (NVIDIA Container
  Toolkit).
- Esse serviço passa a ser "o microsserviço de visão computacional" dentro da futura
  arquitetura.

### Fase 3 — Banco de dados dedicado
- Escolher o SGBD (opções apresentadas ao usuário no chat).
- Modelar entidades mínimas: Partida, Jogador, Time, Evento (cesta/lance
  livre/falta), Súmula.
- Subir o banco como serviço Docker próprio, com volume persistente.
- Ensinar migrations (ferramenta depende da linguagem do backend escolhida).

### Fase 4 — Backend/API
- Linguagem a escolher (opções no chat).
- API expõe endpoints para: receber eventos do serviço de IA, consultar súmula,
  gerenciar partidas/jogadores.
- Comunicação entre IA (Fase 2) e API: a definir (fila de mensagens, REST interno,
  webhook) — bom tópico de arquitetura para estudar mais adiante.

### Fase 5 — Frontend Web
- Linguagem/framework a escolher (opções no chat).
- Consome a API (Fase 4), exibe súmula em tempo real.

### Fase 6 — Orquestração via Docker Compose
- `docker-compose.yml` único subindo IA + backend + frontend + banco.
- Paridade Linux/Windows validada (o mesmo compose funciona nos dois SOs).

### Fase 7 — Segurança aplicada (estudo prático, transversal)
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
2. Decidir GitHub: repositório público ou privado, nome do repositório (Fase 1).
3. Instalar toolchain do Rust (`rustup`) — a confirmar se localmente ou só dentro do
   container Docker.
