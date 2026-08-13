# Banco de dados — PostgreSQL

## Schema

| Tabela/View | O que guarda |
|---|---|
| `times` | Equipes que jogam partidas |
| `jogadores` | Jogadores, cada um vinculado a um time |
| `partidas` | Confrontos entre dois times, com modalidade (3x3/5x5) e status |
| `eventos` | Cestas (2/3 pts), lances livres e faltas — a fonte da verdade de tudo que acontece numa partida |
| `vw_sumula` (view) | Súmula: pontos totais e faltas por jogador em cada partida, **calculada a partir de `eventos`**, não guardada separadamente |

Decisão de design: o placar e a súmula nunca são guardados como número solto
em `partidas` ou em outra tabela — são sempre somados a partir de
`eventos`. Isso evita que o "placar salvo" e o "placar real" (soma dos
eventos) fiquem dessincronizados.

## Migrations

As migrations ficam em `migrations/*.sql`, numeradas em ordem
(`0001_...`, `0002_...`). Convenção compatível com o
[sqlx-cli](https://github.com/launchbadge/sqlx/tree/main/sqlx-cli) do
backend Rust (Fase 4):

```bash
# a partir da Fase 4, dentro de backend/, com DATABASE_URL configurada:
sqlx migrate run
```

**Hoje (antes da Fase 4 existir)**, essas mesmas migrations também são
montadas em `/docker-entrypoint-initdb.d` no `docker-compose.yml` — a
imagem oficial do Postgres roda todo `.sql` dali automaticamente, mas
**só na primeira inicialização do volume** (banco vazio). Isso é só um
atalho de bootstrap para já ter o schema disponível para testes agora;
não é como migrations funcionam de verdade em produção (lá, cada mudança de
schema vira uma migration nova, aplicada de forma controlada e
versionada pela ferramenta, não pelo container do banco).

## Subir o banco localmente

```bash
cp .env.example .env   # e troque a senha
docker compose up -d db
docker compose exec db psql -U basquete -d placar_basquete -c '\dt'
```
