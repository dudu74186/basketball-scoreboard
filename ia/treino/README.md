# Treino do modelo de detecção

## Estratégia: dataset híbrido

Treinar YOLO é rápido. O que custa é ter imagens anotadas — anotar bola e aro
quadro a quadro é trabalho de semanas. Por isso a ordem aqui é:

1. Treinar com um **dataset público** de basquete (grátis, pronto).
2. Rodar o modelo **nos seus vídeos reais** e ver onde ele erra.
3. Anotar **só os casos difíceis** que aparecerem.

O passo 2 é o que dá valor: as métricas do treino falam sobre o dataset
público — outra quadra, outra câmera, outra luz. O que importa é o
desempenho no seu vídeo.

## Passo a passo

```bash
cd ia/treino/
pip install -r requirements.txt
```

**1. Chave do Roboflow** (conta gratuita em https://roboflow.com,
em Settings → API Keys). Coloque em `ia/.env`, que não é versionado:

```
ROBOFLOW_API_KEY=sua-chave-aqui
```

**2. Baixar o dataset**

```bash
python baixar_dataset.py
```

Padrão: [`computer-vision-d5fjh/basketball-detection-dn6fg`](https://universe.roboflow.com/computer-vision-d5fjh/basketball-detection-dn6fg),
**versão 4** — 7.486 imagens (6.017 treino / 981 validação / 488 teste),
classes `ball`, `basket` e `person`, distribuição equilibrada
(~4.900 / ~4.800 / ~4.000 caixas).

> ⚠️ **Confira a versão antes de baixar.** Um projeto do Roboflow tem
> várias versões, e a página do Universe mostra o total do *projeto*, não o
> de cada versão. A v1 deste dataset tem só **499** imagens — 15x menos que
> a v4. Para listar as versões:
>
> ```python
> p = rf.workspace(WORKSPACE).project(PROJETO)
> for v in p.versions(): print(v.id, v.images)
> ```

Para usar outro dataset, basta ajustar as variáveis — o endereço de
qualquer dataset do Universe segue
`universe.roboflow.com/<WORKSPACE>/<PROJETO>/dataset/<VERSAO>`:

```bash
RF_WORKSPACE=outro RF_PROJETO=outro-projeto RF_VERSAO=3 python baixar_dataset.py
```

**3. Treinar**

```bash
export DATA_YAML=../datasets/basketball-detection-dn6fg/data.yaml
python treinar.py
```

Padrões calibrados para a GTX 1650 (4 GB): `yolo11n`, 640px, batch 8,
precisão mista. Ajuste pelo ambiente se precisar:

```bash
EPOCAS=100 BATCH=4 python treinar.py     # se der "CUDA out of memory"
```

**4. Avaliar no vídeo real** — o passo que orienta o resto

```bash
PESOS=../outputs/treino/bola_aro_v1/weights/best.pt \
VIDEO_SOURCE=../samples/teste.mp4 \
python avaliar.py
```

Resume quantas vezes cada classe apareceu e em que porcentagem dos frames.
Sinais de problema: o **aro** deveria estar em quase todo frame (é fixo na
quadra) — se não estiver, o modelo não generalizou para a sua câmera.

## O que vem depois

Detectar bola e aro num frame é uma coisa; decidir **"isso foi uma cesta"**
é outra, e não é IA — é lógica temporal sobre a trajetória (bola cruzando o
aro de cima para baixo). É onde nascem os falsos positivos: rebote, bola
passando na frente do aro, tabela.

Ordem completa da fase de IA no diário do projeto: bola+aro → rastreamento
de jogadores → 2 ou 3 pontos por homografia → número de camisa (OCR) por
último.

## O que não é versionado

`ia/datasets/` (milhares de imagens, rebaixáveis) e os pesos `.pt` gerados.
Ver `.gitignore` na raiz.

## Acompanhar um treino em andamento

```bash
cd ia/treino/
python status.py          # imprime uma vez
python status.py -w       # fica atualizando até o treino acabar
python status.py -w -n 30 # atualizando a cada 30s (padrão: 15s)
python status.py --linha  # uma linha só, para tmux/polybar/i3blocks
```

Mostra se o processo está vivo, quantas épocas faltam, o tempo estimado e a
evolução do mAP50. No modo `-w` o painel é redesenhado no lugar, sem
empilhar; `Ctrl+C` sai do monitor **sem parar o treino**, que roda em outro
processo. Quando o treino termina, o monitor percebe e encerra sozinho.

Exemplo do modo `--linha`, para colar numa barra de status:

```
🏀 2/60 · mAP50 0.919 · 4:12:34
``` O que interessa olhar é se o mAP50 **ainda está subindo**:
se estagnou, o early stopping encerra sozinho e não adianta esperar mais.

Outras formas, se quiser o detalhe cru:

| Comando | Para quê |
|---|---|
| `tail -f ../outputs/treino/treino_bola_aro_v1.log` | Barra de progresso ao vivo, batch a batch |
| `column -s, -t ../outputs/treino/bola_aro_v1/results.csv \| less -S` | Todas as métricas, época a época |
| `nvidia-smi -l 5` | Uso da GPU, atualizando a cada 5s |
| `xdg-open ../outputs/treino/bola_aro_v1/results.png` | Gráficos das curvas (gerado ao final) |

**Os pesos são salvos a cada época** em `weights/best.pt`, então dá para
avaliar um modelo parcial sem esperar o treino inteiro:

```bash
PESOS=../outputs/treino/bola_aro_v1/weights/best.pt python avaliar.py
```

## Vídeos para revisão humana (`ia/revisao/`)

Fica fora do Git (tudo ali é gerado). Organizada na ordem do pipeline —
cada etapa só faz sentido depois que a anterior está boa:

| Pasta | Pergunta que responde |
|---|---|
| `01_deteccao/` | O modelo está vendo bola, aro e jogadores? |
| `02_rastreamento/` | A bola tem trajetória contínua ou vira pontos soltos? |
| `03_cestas/` | Os eventos marcados são cestas de verdade? |
| `04_falhas/` | O que exatamente precisa ser ensinado ao modelo? |

O `04_falhas/` alimenta a anotação no CVAT: em vez de anotar frames
aleatórios, anota-se o que comprovadamente falha. Detalhes do que observar
em cada pasta estão em `ia/revisao/LEIA-ME.md`.

Convenção de nome: `<data>_<assunto>_<detalhe>.mp4`, ex.:
`20260815_deteccao_1080p.mp4`.

## Rastreamento e trajetória da bola

```bash
cd ia/treino/
python avaliar_rastreamento.py              # compara os níveis
INICIO=1800 DURACAO=90 python avaliar_rastreamento.py
```

⚠️ **O ByteTrack foi testado e descartado.** A intuição dizia que um
rastreador ajudaria; a medição (60s do vídeo de referência) disse o
contrário:

| abordagem | frames com bola | maior sequência |
|---|---|---|
| detecção pura | 571 (31,7%) | 5,0s |
| + ByteTrack | **493 (27,4%)** | 5,0s |
| + ByteTrack + interpolação | 679 (37,7%) | 7,1s |
| **detecção pura + interpolação** | **841 (46,7%)** | **7,1s** |

O rastreador piorou a cobertura em 14%: ele só emite um track depois de
confirmá-lo em vários frames seguidos, descartando detecções isoladas — que
é justamente o que temos. Também trocou de ID 20 vezes em 60s.

Quem dá o ganho é a **interpolação de lacunas** (`ia/rastreamento.py`), e
ela não precisa de rastreador. Vale reavaliar o ByteTrack se um dia a
detecção da bola ficar consistente.

## Juntando o dataset próprio ao público

Depois de exportar do CVAT (formato **YOLOv8 Detection**, com *Save images*),
descompacte uma pasta por tarefa em `ia/datasets/proprio/` e rode:

```bash
cd ia/treino/
python juntar_datasets.py
DATA_YAML=../datasets/combinado.yaml NOME_RUN=bola_aro_v2 python treinar.py
```

⚠️ O script **recusa a juntar** se a ordem das classes divergir entre os
datasets. Não é excesso de zelo: os labels YOLO guardam o índice numérico,
não o nome. Com `ball` sendo 0 num e 1 no outro, o treino aprende trocado
e **não emite erro** — o prejuízo só aparece no resultado, horas depois.

A validação usa **apenas o dataset público**, de propósito: manter a mesma
régua é o que permite comparar o modelo novo com o `bola_aro_v1`.

### Se o export do CVAT vier sem imagens

É fácil esquecer de marcar *Save images* e receber um zip só com os `.txt`.
Como o vídeo de origem está aqui, não precisa refazer:

```bash
python importar_cvat.py "../datasets/Video 1.zip" ../revisao/04_falhas/fp_01_t3692s.mp4 clipe1
```

O script extrai os frames do vídeo e os pareia com os labels pelo número do
frame. ⚠️ Confira que o vídeo passado é mesmo o que foi anotado — parear
labels de um clipe com imagens de outro produz lixo silenciosamente. Um
jeito de verificar é comparar a posição do aro anotado com a detectada no
vídeo: devem coincidir.
