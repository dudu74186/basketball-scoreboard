# 🖥️ Requisitos de Máquina — Linux e Windows

> Levantamento feito em 11/08/2026, referente à Fase 0 de [[linha_do_tempo]].
> Objetivo: paridade de ambiente entre os dois SOs do usuário via Docker.

## Verificação feita na máquina Linux (Arch) — 11/08/2026

| Ferramenta | Status | Versão |
|---|---|---|
| Docker | ✅ Instalado, serviço ativo, grupo `docker` aplicado e confirmado com `docker run hello-world` em 11/08/2026 | 29.7.2 |
| Git | ✅ instalado | 2.54.0 |
| Python | ✅ instalado (miniconda) | 3.13.13 |
| Node.js | ✅ instalado | v26.2.0 |
| Java | ❌ Não instalado | — |
| Go | ❌ Não instalado | — |
| Rust/cargo | ❌ Não instalado | — |
| .NET | ❌ Não instalado | — |
| VSCode (`code` CLI) | ❌ Não instalado | — |
| psql / mysql (clientes DB) | ❌ Não instalado | — |
| adb (Android) | ❌ Não instalado | — |
| GPU NVIDIA | ✅ GTX 1650, 4GB, driver 610.43.03 | |
| RAM / Disco livre | ✅ 23GB RAM / 343GB livres | |

**Conclusão:** a máquina tem folga de recursos (RAM/disco) para rodar Docker + vários
containers. O único item crítico e imediato é instalar o **Docker**. As demais
linguagens só devem ser instaladas depois que o usuário escolher quais vai usar —
ver perguntas no chat principal.

## Atualização 11/08/2026 (sessão Claude) — Docker instalado, faltou o grupo

Docker Engine + Compose já estavam instalados e o serviço `docker` já estava
`active` nesta máquina. O bloqueio real era permissão: `docker run hello-world`
falhava com `permission denied ... docker.sock` porque o usuário `eduardo` ainda
não pertencia ao grupo `docker`.

Diagnóstico feito:
- `getent group docker` mostrava `docker:x:962:` (grupo vazio) — ou seja, o
  `sudo usermod -aG docker $USER` do passo original nunca tinha sido executado
  com sucesso antes desta sessão.
- Uma primeira tentativa do usuário (`sudo usermod -aG docker $USER`) não
  alterou o `/etc/group` (motivo não identificado — possivelmente a variável
  `$USER` ou a senha do sudo).
- Rodando explicitamente `sudo usermod -aG docker eduardo` (com o nome do
  usuário literal em vez de `$USER`), a senha foi aceita e `/etc/group` passou
  a mostrar `docker:x:962:eduardo` — grupo aplicado com sucesso.

**Atualização (mesmo dia, 11/08/2026):** o usuário rodou `docker run hello-world`
e recebeu a mensagem de sucesso ("Hello from Docker!"), confirmando que a
imagem foi baixada, o container criado e executado, e a saída streamada de
volta ao terminal. Grupo `docker` está funcionando corretamente. **Docker
está com a instalação 100% validada.** Falta só GitHub para fechar a Fase 0
de [[linha_do_tempo]] e, mais adiante, o `nvidia-container-toolkit` para a
Fase 2.

## Passo 1 (agora): instalar Docker no Linux (Arch)

Como é uma alteração de sistema (precisa de `sudo`), o usuário deve rodar isto no
próprio terminal (pode usar `!` no Claude Code para executar e trazer o resultado
de volta ao chat):

```bash
# Instala o Docker Engine + plugin do Compose
sudo pacman -Syu docker docker-compose

# Habilita e inicia o serviço
sudo systemctl enable --now docker

# Permite rodar docker sem sudo (adiciona seu usuário ao grupo docker)
sudo usermod -aG docker $USER

# Depois disso, é preciso fazer logout/login (ou reiniciar) para o grupo valer
```

Para usar a GPU NVIDIA dentro de containers (necessário na Fase 2, para o serviço de
IA), depois também será preciso o `nvidia-container-toolkit`:

```bash
sudo pacman -S nvidia-container-toolkit
sudo systemctl restart docker
```

Validar a instalação:

```bash
docker --version
docker compose version
docker run hello-world
```

## Passo 1 no Windows (quando for programar por lá)

1. Ativar o **WSL2** (Windows Subsystem for Linux) — pré-requisito do Docker Desktop.
   ```powershell
   wsl --install
   ```
2. Instalar o **Docker Desktop for Windows**, com a integração WSL2 habilitada.
3. Garantir que o Docker Desktop está configurado para usar o backend WSL2 (não
   Hyper-V puro), para melhor compatibilidade com o que for feito no Linux.
4. Se for usar a GPU NVIDIA no Windows também, instalar os drivers com suporte a
   CUDA-on-WSL.

Isso garante que o mesmo `docker-compose.yml` do repositório funcione igual nos dois
sistemas — esse é o ponto principal de usar Docker aqui.

## Ferramentas que dependem de escolha do usuário (ainda não instalar)

Estas só entram depois que o usuário decidir a linguagem de cada camada (perguntas no
chat principal). Listado aqui só para referência futura, **nenhuma foi instalada**:

- Backend: runtime/SDK da linguagem escolhida (ex.: Node.js já está instalado; Go,
  Java/JDK, Rust ou .NET SDK dependem da escolha).
- Frontend: depende de Node.js (já instalado) se a escolha for algo do ecossistema
  JS/TS.
- Banco de dados: não precisa instalar cliente nativo — vai rodar como container
  Docker. Só um cliente GUI opcional (ex.: DBeaver, TablePlus) se o usuário quiser.
- Mobile/Android: Android Studio + JDK + SDK do Android, ou Flutter SDK, dependendo da
  escolha.
- Editor: `code` (VSCode) não está instalado — perguntar se é essa a preferência antes
  de instalar.

## Regra de ouro
Nenhuma linguagem ou ferramenta desta lista de "dependem de escolha" deve ser
instalada ou usada em código sem confirmação explícita do usuário — ver
[[autorizacoes]].
