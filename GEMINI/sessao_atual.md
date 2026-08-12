# 📝 Registro de Sessão - Placar Automático de Basquete

Este arquivo documenta o progresso da nossa colaboração, incluindo aulas didáticas, perguntas pendentes e o status atual do projeto.

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
1. Decidir com o usuário: repositório GitHub público ou privado, e o nome do
   repositório (Fase 1 de [[linha_do_tempo]]).
2. Criar a estrutura de pastas do monorepo (`ia/`, `backend/`, `frontend/`,
   `docker/` etc.) e iniciar o versionamento.
3. Instalar o toolchain do Rust (`rustup`) — decidir se local ou só em
   container.
