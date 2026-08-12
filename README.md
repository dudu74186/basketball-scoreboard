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

## Status

Projeto em desenvolvimento inicial. Consulte o histórico de decisões, fases e
pendências no diário de bordo do projeto.

## Como rodar (por enquanto)

Só o serviço de IA existe até o momento:

```bash
cd ia/
python main.py
```

Requer um ambiente Python com `ultralytics` e `opencv-python` instalados
(recomenda-se Conda; ver ambiente `placar_basquete`, Python 3.10, com PyTorch +
CUDA para aceleração por GPU).

## Licença

A definir.
