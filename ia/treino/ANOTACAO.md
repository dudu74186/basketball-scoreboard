# Anotação dos vídeos com CVAT

## Por que CVAT, e não uma ferramenta nossa

Chegamos a considerar construir a ferramenta de anotação dentro do frontend
do projeto. A decisão foi usar o [CVAT](https://www.cvat.ai/) por três
motivos concretos:

1. **Interpolação entre keyframes.** Numa quadra o aro não se mexe: você o
   marca em dois frames e o CVAT preenche todos os do meio. Corta 60–80% do
   tempo em tarefas de rastreamento. Uma ferramenta nossa, feita do zero,
   exigiria marcar frame a frame.
2. **Auto-anotação nativa com YOLO da Ultralytics** — é a "pré-marcação da
   IA" que queríamos, já pronta.
3. **É self-hosted por Docker Compose**, então continua coerente com o
   ambiente containerizado do projeto.

O que **não** delegamos ao CVAT: a tela de revisão dos eventos de uma
partida (ver as detecções sobre o vídeo e confirmar/corrigir a súmula). Isso
é específico deste projeto e será construído no nosso frontend.

## Onde o CVAT está instalado

**Fora do repositório**, em `~/ferramentas/cvat`. Ele é uma ferramenta de
trabalho, não parte do produto — misturar seus ~10 serviços ao
`docker-compose.yml` do projeto tornaria os dois mais difíceis de manter.

### Instalação (já feita, registrada para reprodução)

```bash
mkdir -p ~/ferramentas && cd ~/ferramentas
git clone --depth 1 https://github.com/cvat-ai/cvat.git
cd cvat
```

O CVAT publica na porta **8080**, que já é do frontend deste projeto. Em vez
de editar o `docker-compose.yml` deles (que seria desfeito no próximo
`git pull`), criamos `~/ferramentas/cvat/docker-compose.override.yml` — o
Compose lê esse arquivo automaticamente:

```yaml
services:
  traefik:
    ports: !override
      - 8081:8080
      - 8090:8090
```

O `!override` é obrigatório: por padrão o Compose **soma** as listas de
`ports`, e sem ele a 8080 continuaria publicada, mantendo o conflito.

```bash
docker compose up -d
```

### Portas em uso, para não confundir

| Porta | Serviço |
|---|---|
| 8080 | Frontend do Placar Automático |
| 3000 / 50051 | API (REST / gRPC) |
| 5432 | PostgreSQL |
| **8081** | **CVAT** |

## Fluxo de anotação

**1. Criar o usuário administrador** (só na primeira vez)

```bash
cd ~/ferramentas/cvat
docker compose exec cvat_server bash -ic \
  'python3 ~/manage.py createsuperuser'
```

**2. Abrir** http://localhost:8081 e entrar com esse usuário.

**3. Criar um projeto** com as classes que vamos detectar. Comece pelas duas
que interessam na primeira etapa:

- `bola`
- `aro`

(`jogador` e `arbitro` entram na etapa seguinte — ver a ordem da fase de IA
no diário do projeto. Se quiser já deixar criadas, não atrapalha.)

**4. Criar uma tarefa** e subir o vídeo. Os vídeos do projeto estão em:

- `ia/samples/teste.mp4` — curto, bom para começar
- `COMETAS X CESB - RODADA 16 - LCB 2021.mp4` (na raiz de
  `~/Documentos/Python`) — jogo real completo

Dica: use **frame step** (ex.: 1 a cada 10) ao criar a tarefa. Frames
consecutivos são quase idênticos e não agregam ao treino — só dão trabalho.

**5. Auto-anotar com YOLO** para não começar do zero. O modelo genérico
`yolo11n` já detecta pessoa e bola de fábrica; o aro precisará ser feito à
mão até existir o primeiro modelo treinado.

**6. Corrigir usando track mode + interpolação.** Para o aro: marque num
frame, marque de novo no último, e deixe a interpolação preencher.

**7. Exportar** no formato **YOLO** e descompactar em
`ia/datasets/proprio/`.

## Juntando com o dataset público

A estratégia é híbrida (ver `README.md` desta pasta): o dataset público dá o
volume, o seu dá a especificidade da sua quadra e câmera. Para treinar com
os dois, aponte o `data.yaml` para as duas pastas:

```yaml
train:
  - ../datasets/basketball-detection-dn6fg/train/images
  - ../datasets/proprio/train/images
val:
  - ../datasets/basketball-detection-dn6fg/valid/images
```

⚠️ **Os nomes e a ORDEM das classes precisam ser idênticos nos dois
datasets.** Os arquivos de label YOLO guardam o índice numérico da classe,
não o nome — se `bola` for 0 num dataset e 1 no outro, o treino aprende
errado sem dar nenhum erro. É o tipo de bug que só aparece no resultado
ruim, então confira os dois `data.yaml` antes de treinar.

## Desligando o CVAT

Ele consome memória à toa quando não está em uso:

```bash
cd ~/ferramentas/cvat && docker compose stop
```
