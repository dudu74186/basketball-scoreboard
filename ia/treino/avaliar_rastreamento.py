#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mede se o rastreamento realmente melhora a continuidade da bola.

Compara três níveis sobre o MESMO trecho:

  1. detecção pura      — `predict`, cada frame isolado
  2. + rastreamento     — `track` (ByteTrack), que reaproveita detecções de
                          baixa confiança na segunda passada de associação
  3. + interpolação     — preenche lacunas curtas entre posições conhecidas

A pergunta que isso responde: dá para montar uma trajetória contínua o
bastante para decidir se houve cesta?

Uso:
    INICIO=3060 DURACAO=60 python avaliar_rastreamento.py
"""

import os
import sys
from pathlib import Path

RAIZ_IA = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_IA))

from deteccao import CONF, IMGSZ, eh_falso_positivo  # noqa: E402
from rastreamento import (  # noqa: E402
    LACUNA_MAX,
    RASTREADOR,
    interpolar_lacunas,
    maior_sequencia,
)

PESOS = os.environ.get("PESOS", str(RAIZ_IA / "outputs" / "treino" / "bola_aro_v1" / "weights" / "best.pt"))
VIDEO = os.environ.get("VIDEO_SOURCE", str(RAIZ_IA / "samples" / "circuito_capixaba_final_bronze.mp4"))
INICIO = int(os.environ.get("INICIO", "3060"))
DURACAO = int(os.environ.get("DURACAO", "60"))


def recortar(origem: str, destino: Path) -> bool:
    import subprocess

    destino.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(INICIO),
         "-i", origem, "-t", str(DURACAO), "-c", "copy", str(destino)],
        capture_output=True,
    )
    return r.returncode == 0


def coletar(modelo, clipe: str, rastreando: bool) -> tuple[dict, set, int]:
    """Devolve (posições da bola por frame, IDs vistos, total de frames)."""
    posicoes: dict[int, tuple[float, float]] = {}
    ids: set[int] = set()

    if rastreando:
        fluxo = modelo.track(clipe, conf=CONF, imgsz=IMGSZ, verbose=False,
                             stream=True, persist=True, tracker=RASTREADOR)
    else:
        fluxo = modelo.predict(clipe, conf=CONF, imgsz=IMGSZ, verbose=False,
                               stream=True)

    total = 0
    for n, r in enumerate(fluxo):
        total += 1
        altura = r.orig_shape[0]
        for i, (cls, caixa) in enumerate(zip(r.boxes.cls, r.boxes.xywh)):
            if modelo.names[int(cls)] != "ball":
                continue
            cx, cy = float(caixa[0]), float(caixa[1])
            if eh_falso_positivo("ball", cy, altura):
                continue
            # Quando há várias "bolas" no frame, fica a de maior confiança
            # (o loop já vem ordenado por confiança decrescente).
            posicoes.setdefault(n, (cx, cy))
            if rastreando and r.boxes.id is not None:
                ids.add(int(r.boxes.id[i]))

    return posicoes, ids, total


def linha(rotulo: str, frames_com_bola: int, total: int, seq: int) -> str:
    return (f"  {rotulo:<24} {frames_com_bola:>6} ({100*frames_com_bola/total:>5.1f}%)"
            f"   maior sequência: {seq:>4} frames ({seq/30:.1f}s)")


def main() -> int:
    if not Path(PESOS).exists():
        print(f"pesos não encontrados: {PESOS}", file=sys.stderr)
        return 1
    if not Path(VIDEO).exists():
        print(f"vídeo não encontrado: {VIDEO}", file=sys.stderr)
        return 1

    clipe = RAIZ_IA / "outputs" / "_clipe_rastreamento.mp4"
    print(f"recortando {DURACAO}s a partir de {INICIO}s…")
    if not recortar(VIDEO, clipe):
        print("falha ao recortar o vídeo", file=sys.stderr)
        return 1

    from ultralytics import YOLO

    modelo = YOLO(PESOS)
    print(f"imgsz={IMGSZ}  conf={CONF}  rastreador={RASTREADOR}"
          f"  lacuna_max={LACUNA_MAX} frames\n")

    print("processando sem rastreamento…")
    pos_det, _, total = coletar(modelo, str(clipe), rastreando=False)

    print("processando com rastreamento…")
    pos_rast, ids, _ = coletar(modelo, str(clipe), rastreando=True)

    pos_interp = interpolar_lacunas(pos_rast)

    print(f"\n  {total} frames analisados\n")
    print(linha("1. detecção pura", len(pos_det), total, maior_sequencia(set(pos_det))))
    print(linha("2. + rastreamento", len(pos_rast), total, maior_sequencia(set(pos_rast))))
    print(linha("3. + interpolação", len(pos_interp), total, maior_sequencia(set(pos_interp))))

    print(f"\n  IDs distintos atribuídos à bola: {len(ids)}")
    print("  (poucos IDs = trajetória estável; muitos = o rastreador perde e")
    print("   recomeça, o que quebra a continuidade)")

    ganho = len(pos_interp) - len(pos_det)
    if len(pos_det):
        print(f"\n  ganho total: +{ganho} frames com bola "
              f"({100*ganho/len(pos_det):+.0f}% sobre a detecção pura)")

    clipe.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
