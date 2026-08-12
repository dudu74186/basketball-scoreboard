# Sugestões do Gemini

Este arquivo centraliza todas as propostas técnicas para o projeto, organizadas por categorias.

> ⚠️ **Revisão de 11/08/2026:** o escopo do projeto mudou (ver [[linha_do_tempo]]). As
> sugestões abaixo, feitas na sessão de 21/05/2026, foram o ponto de partida mas **não
> valem mais como decisão fechada** nos itens de Backend/Web e Banco de Dados — o
> usuário decidiu desacoplar frontend/backend, usar um banco dedicado (não SQLite) e
> variar as linguagens do projeto. Mantidas aqui como histórico. As opções atuais em
> aberto (backend, frontend, banco, mobile) estão sendo escolhidas pelo usuário no chat
> principal — nenhuma foi aplicada ainda.

## 🛠️ Ferramentas (histórico — 21/05/2026)
- **Visão Computacional:** **YOLOv11** (You Only Look Once). É a versão mais atual e eficiente para detecção de objetos em tempo real. Como você tem GPUs NVIDIA, usaremos a versão que roda via **CUDA** para máxima performance. *(Ainda válido — este componente segue em Python/YOLO, ver Fase 2 de [[linha_do_tempo]].)*
- **Processamento de Imagem:** **OpenCV**. Essencial para manipular os frames do vídeo, desenhar as caixas de detecção e gerenciar a conexão com a câmera. *(Ainda válido.)*
- ~~**Backend/Web:** Flask.~~ *(Superado: backend agora é uma API separada do frontend, linguagem a escolher.)*
- ~~**Banco de Dados:** SQLite.~~ *(Superado: banco dedicado containerizado, engine a escolher.)*

## 🏗️ Infraestrutura (histórico — 21/05/2026)
- **Comunicação Celular-PC:** **IP Webcam** (Android) ou **Iriun Webcam**. Transformam o celular em uma câmera IP que o Python consegue ler como um fluxo de vídeo (URL). *(Ainda válido.)*
- **Aceleração de Hardware:** **NVIDIA CUDA Toolkit & cuDNN**. Necessários para o processamento de vídeo pela GPU. *(Ainda válido — GPU real na máquina é uma GTX 1650 4GB, não a GTX 1660 Super citada originalmente; ver [[requisitos_ambiente]].)*
- ~~**Frontend:** HTML/CSS com Jinja2.~~ *(Superado: frontend web desacoplado, framework a escolher.)*

## 🧠 Inteligência Artificial (ainda válido)
- **Detecção de Objetos:** Treinar um modelo específico (ou usar pré-treinados) para: `Bola`, `Aro`, `Jogador`.
- **OCR (Reconhecimento de Texto):** **EasyOCR** ou o próprio módulo de classificação do YOLO para ler os números das camisas.
- **Lógica de Cesta:** Algoritmo de **Rastreamento de Trajetória**. A IA monitora se a "caixa" da bola cruzou a "caixa" do aro de cima para baixo.

## 🌐 Infraestrutura nova (a partir de 11/08/2026)
- **Versionamento/backup:** GitHub (repositório a criar — Fase 1 de [[linha_do_tempo]]).
- **Ambiente containerizado:** Docker + Docker Compose, para paridade entre Linux e
  Windows (ver [[requisitos_ambiente]] para instalação).
- **Arquitetura:** múltiplos serviços containerizados (IA, backend/API, frontend,
  banco de dados) orquestrados via `docker-compose.yml`.
- **Segurança:** tratada como estudo transversal a partir da Fase 7 de
  [[linha_do_tempo]] (HTTPS, autenticação, gestão de segredos, scan de dependências e
  imagens Docker, OWASP Top 10).
- **Backend, Frontend, Banco de dados, Mobile:** opções apresentadas ao usuário no
  chat principal em 11/08/2026.

### ✅ Decisão: Backend em Rust (11/08/2026)
- Escolhido pelo usuário após análise específica do requisito de streaming de vídeo
  em tempo real + comunicação de alta performance com o serviço de IA (YOLO).
- Motivo: melhor combinação de desempenho (equivalente a C/C++) e segurança de
  memória de toda a lista avaliada (Go, Rust, C#/.NET, Node.js/TS, Java/Spring).
- Padrão de comunicação recomendado com o serviço Python/YOLO: **gRPC** (binário,
  suporte nativo a streaming), via crate `tonic`. WebRTC no lado Rust via
  `webrtc-rs`, se necessário para ingestão do vídeo do celular.

### ✅ Decisão: Frontend em TypeScript + React (11/08/2026)
- Consome a API Rust. Resultados em tempo real via WebSocket (ou gRPC-Web/Connect,
  a avaliar na Fase 5).

### ✅ Decisão: Banco de dados PostgreSQL (11/08/2026)
- Roda como serviço próprio em container Docker (Fase 3).
- Acesso a partir do backend Rust via crate `sqlx` (ou `sea-orm` como alternativa
  com ORM mais completo, a decidir na Fase 3 com o usuário).
- Entidades mínimas a modelar: Partida, Time, Jogador, Evento (cesta 2pts/3pts,
  lance livre, falta), Súmula.

### ✅ Decisão: App Android em Kotlin nativo (11/08/2026)
- Meta de longo prazo (Fase 9). Consome a mesma API Rust usada pelo frontend web.

**Stack completo decidido:** Python (IA/YOLO) + Rust (backend/API + gRPC) +
TypeScript/React (frontend) + PostgreSQL (banco) + Kotlin (app Android futuro),
tudo orquestrado via Docker/Docker Compose e versionado no GitHub.
