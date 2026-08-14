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

Padrão: [`computer-vision-d5fjh/basketball-detection-dn6fg`](https://universe.roboflow.com/computer-vision-d5fjh/basketball-detection-dn6fg)
(~4.900 imagens, classes de pessoa, bola e aro). Para usar outro, basta
ajustar as variáveis — o endereço de qualquer dataset do Universe segue
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
