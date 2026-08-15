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

# Resolução de inferência e filtro do placar vêm de ia/deteccao.py, para a
# avaliação medir exatamente o que o serviço de inferência vai aplicar.
sys.path.insert(0, str(RAIZ_IA))
from deteccao import CONF, FAIXA_PLACAR, IMGSZ, eh_falso_positivo  # noqa: E402


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
    print(f"avaliando {Path(VIDEO).name}")
    print(f"  1 frame a cada {PULO}  ·  conf>={CONF}  ·  imgsz={IMGSZ}"
          f"  ·  faixa do placar ignorada: {FAIXA_PLACAR:.0%}\n")

    total_por_classe = Counter()
    frames_com_classe = Counter()
    descartadas = Counter()
    frames = 0

    resultados = modelo.predict(
        VIDEO, stream=True, conf=CONF, verbose=False, vid_stride=PULO, imgsz=IMGSZ
    )

    for r in resultados:
        frames += 1
        altura = r.orig_shape[0]
        presentes = set()
        for cls, caixa in zip(r.boxes.cls, r.boxes.xywh):
            classe = nomes[int(cls)]
            if eh_falso_positivo(classe, float(caixa[1]), altura):
                descartadas[classe] += 1
                continue
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

    if descartadas:
        total_desc = sum(descartadas.values())
        print(f"\n  {total_desc} detecções descartadas pelo filtro do placar "
              f"({dict(descartadas)})")

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
