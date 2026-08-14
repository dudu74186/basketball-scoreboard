#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Roda o modelo treinado sobre um vídeo real e resume o que ele detectou.

Este é o passo mais importante da estratégia híbrida: as métricas do treino
(mAP, precisão) dizem como o modelo foi no dataset público — que tem outra
quadra, outra câmera, outra iluminação. O que interessa é como ele se sai
NO SEU vídeo. É daqui que sai a lista do que anotar depois.

Uso:
    PESOS=../outputs/treino/bola_aro_v1/weights/best.pt python avaliar.py
"""

import os
import sys
from collections import Counter
from pathlib import Path

from _ambiente import carregar_env

# Carrega ia/.env antes de qualquer os.environ.get abaixo.
carregar_env()

RAIZ_IA = Path(__file__).resolve().parent.parent

PESOS = os.environ.get("PESOS", str(RAIZ_IA / "outputs" / "treino" / "bola_aro_v1" / "weights" / "best.pt"))
VIDEO = os.environ.get("VIDEO_SOURCE", str(RAIZ_IA / "samples" / "teste.mp4"))
# Só processa 1 frame a cada N: para um diagnóstico não é preciso ver todos,
# e o vídeo inteiro demoraria bem mais.
PULO = int(os.environ.get("PULO", "5"))
CONF = float(os.environ.get("CONF", "0.25"))


def main() -> int:
    if not Path(PESOS).exists():
        print(f"pesos não encontrados: {PESOS}\n  treine antes com treinar.py", file=sys.stderr)
        return 1
    if not Path(VIDEO).exists():
        print(f"vídeo não encontrado: {VIDEO}", file=sys.stderr)
        return 1

    from ultralytics import YOLO

    modelo = YOLO(PESOS)
    nomes = modelo.names
    print(f"classes do modelo: {nomes}")
    print(f"avaliando {Path(VIDEO).name} (1 frame a cada {PULO}, conf>={CONF})…\n")

    total_por_classe = Counter()
    frames_com_classe = Counter()
    frames = 0

    resultados = modelo.predict(
        VIDEO, stream=True, conf=CONF, verbose=False, vid_stride=PULO
    )

    for r in resultados:
        frames += 1
        presentes = set()
        for caixa in r.boxes:
            classe = nomes[int(caixa.cls)]
            total_por_classe[classe] += 1
            presentes.add(classe)
        for classe in presentes:
            frames_com_classe[classe] += 1

    if frames == 0:
        print("nenhum frame processado.", file=sys.stderr)
        return 1

    print(f"{frames} frames analisados\n")
    print(f"{'classe':<16}{'detecções':>11}{'por frame':>11}{'% frames':>10}")
    print("-" * 48)
    for classe in sorted(total_por_classe, key=total_por_classe.get, reverse=True):
        total = total_por_classe[classe]
        pct = 100 * frames_com_classe[classe] / frames
        print(f"{classe:<16}{total:>11}{total / frames:>11.2f}{pct:>9.1f}%")

    print(
        "\nO que olhar:\n"
        "  - 'aro' deveria aparecer em quase todo frame (é fixo na quadra).\n"
        "    Se a % for baixa, o modelo não generalizou para a sua câmera.\n"
        "  - 'bola' em bem menos frames é normal (sai de quadra, é ocultada).\n"
        "  - Muitas detecções por frame de uma classe que deveria ser única\n"
        "    (o aro) indica falso positivo."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
