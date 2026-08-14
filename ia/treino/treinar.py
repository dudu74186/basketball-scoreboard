#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Treina o modelo de detecção sobre o dataset baixado.

Os padrões aqui são calibrados para a GTX 1650 (4 GB de VRAM):
modelo nano, 640px e batch pequeno. Modelos m/l/x não cabem nessa placa.

Uso:
    python treinar.py                          # usa os padrões
    EPOCAS=100 BATCH=8 python treinar.py       # ajusta pelo ambiente
"""

import os
import sys
from pathlib import Path

from _ambiente import carregar_env

# Carrega ia/.env antes de qualquer os.environ.get abaixo.
carregar_env()

RAIZ_IA = Path(__file__).resolve().parent.parent

# Caminho do data.yaml gerado pelo baixar_dataset.py.
DATA_YAML = os.environ.get("DATA_YAML", "")

# yolo11n = "nano", o menor da família. Numa placa de 4 GB é a escolha
# realista; o ganho de precisão do 's' raramente compensa o risco de estourar
# a memória. Sempre partindo dos pesos pré-treinados no COCO (transfer
# learning) — treinar do zero exigiria muito mais dados e tempo.
MODELO_BASE = os.environ.get("MODELO_BASE", str(RAIZ_IA / "models" / "yolo11n.pt"))

EPOCAS = int(os.environ.get("EPOCAS", "60"))
IMGSZ = int(os.environ.get("IMGSZ", "640"))
# batch=8 é conservador de propósito. Se sobrar VRAM, subir para 16 acelera;
# se estourar ("CUDA out of memory"), descer para 4.
BATCH = int(os.environ.get("BATCH", "8"))
NOME_RUN = os.environ.get("NOME_RUN", "bola_aro_v1")

SAIDA = RAIZ_IA / "outputs" / "treino"


def main() -> int:
    if not DATA_YAML:
        print(
            "DATA_YAML não definida.\n\n"
            "  Rode antes:  python baixar_dataset.py\n"
            "  Depois:      export DATA_YAML=<caminho>/data.yaml\n",
            file=sys.stderr,
        )
        return 1

    if not Path(DATA_YAML).exists():
        print(f"data.yaml não encontrado: {DATA_YAML}", file=sys.stderr)
        return 1

    from ultralytics import YOLO

    import torch

    if not torch.cuda.is_available():
        # Não é erro fatal — treinar na CPU funciona, só é ordens de grandeza
        # mais lento. Melhor avisar do que deixar rodando a noite toda sem
        # a pessoa perceber.
        print("AVISO: CUDA indisponível, o treino vai rodar na CPU (bem mais lento).")
    else:
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    modelo = YOLO(MODELO_BASE)

    modelo.train(
        data=DATA_YAML,
        epochs=EPOCAS,
        imgsz=IMGSZ,
        batch=BATCH,
        project=str(SAIDA),
        name=NOME_RUN,
        # Precisão mista: usa float16 onde dá, economizando VRAM sem perder
        # qualidade perceptível. Importante nos 4 GB.
        amp=True,
        # Interrompe se não melhorar por 15 épocas seguidas — evita gastar
        # tempo depois que o modelo já convergiu.
        patience=15,
        exist_ok=True,
    )

    print(f"\npesos salvos em {SAIDA / NOME_RUN / 'weights' / 'best.pt'}")
    print("avalie no vídeo real com:  python avaliar.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
