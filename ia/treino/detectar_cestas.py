#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Roda a lógica de cesta num trecho e gera os clipes para conferência.

Cada candidato vira um clipe curto em `ia/revisao/03_cestas/`, com a
trajetória e a linha do aro desenhadas — a decisão final de "foi cesta ou
não" é sua, olhando o vídeo.

Uso:
    python detectar_cestas.py
    INICIO=1800 DURACAO=300 python detectar_cestas.py
"""

import os
import subprocess
import sys
from pathlib import Path

RAIZ_IA = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_IA))

from cestas import detectar_cestas, estabilizar_aro  # noqa: E402
from deteccao import CONF, IMGSZ, eh_falso_positivo  # noqa: E402
from rastreamento import interpolar_lacunas  # noqa: E402

PESOS = os.environ.get("PESOS", str(RAIZ_IA / "outputs" / "treino" / "bola_aro_v1" / "weights" / "best.pt"))
VIDEO = os.environ.get("VIDEO_SOURCE", str(RAIZ_IA / "samples" / "circuito_capixaba_final_bronze.mp4"))
INICIO = int(os.environ.get("INICIO", "3000"))
DURACAO = int(os.environ.get("DURACAO", "180"))
SAIDA = RAIZ_IA / "revisao" / "03_cestas"

# Segundos de contexto antes e depois do cruzamento, em cada clipe.
CONTEXTO = float(os.environ.get("CONTEXTO", "3"))


def recortar(origem: str, destino: Path, inicio: float, duracao: float,
             recodificar: bool = False) -> bool:
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(inicio),
           "-i", str(origem), "-t", str(duracao)]
    # Corte exato exige recodificar; para o clipe grande, copiar é bem mais
    # rápido e a precisão do keyframe basta.
    cmd += ["-c:v", "libx264", "-crf", "23", "-preset", "fast"] if recodificar else ["-c", "copy"]
    cmd.append(str(destino))
    return subprocess.run(cmd, capture_output=True).returncode == 0


def main() -> int:
    for caminho, nome in ((PESOS, "pesos"), (VIDEO, "vídeo")):
        if not Path(caminho).exists():
            print(f"{nome} não encontrado: {caminho}", file=sys.stderr)
            return 1

    SAIDA.mkdir(parents=True, exist_ok=True)
    clipe = RAIZ_IA / "outputs" / "_cestas_trecho.mp4"

    print(f"recortando {DURACAO}s a partir de {INICIO}s…")
    if not recortar(VIDEO, clipe, INICIO, DURACAO):
        print("falha ao recortar", file=sys.stderr)
        return 1

    from ultralytics import YOLO

    modelo = YOLO(PESOS)
    print(f"analisando (imgsz={IMGSZ})…")

    bola: dict[int, tuple[float, float]] = {}
    aros: dict[int, tuple[int, int, int, int]] = {}
    total = 0

    for n, r in enumerate(modelo.predict(str(clipe), conf=CONF, imgsz=IMGSZ,
                                         verbose=False, stream=True)):
        total = n + 1
        altura = r.orig_shape[0]
        for i, cls in enumerate(r.boxes.cls):
            nome = modelo.names[int(cls)]
            cx, cy = float(r.boxes.xywh[i][0]), float(r.boxes.xywh[i][1])
            if nome == "ball" and not eh_falso_positivo("ball", cy, altura):
                bola.setdefault(n, (cx, cy))
            elif nome == "basket":
                aros.setdefault(n, tuple(int(v) for v in r.boxes.xyxy[i]))

    trajetoria = interpolar_lacunas(bola)
    aros_estaveis = estabilizar_aro(aros, total)
    # set(bola) = frames com deteccao real; o resto da trajetoria e interpolado.
    eventos = detectar_cestas(trajetoria, aros_estaveis, reais=set(bola))

    print(f"\n  {total} frames  ·  bola em {len(trajetoria)}"
          f" ({100*len(trajetoria)/total:.0f}%)  ·  aro em {len(aros)} detectados")
    print(f"  candidatos a cesta: {len(eventos)}\n")

    if not eventos:
        print("  nenhum candidato — considere afrouxar os parâmetros em ia/cestas.py")
        clipe.unlink(missing_ok=True)
        return 0

    for n, ev in enumerate(eventos, 1):
        segundo = ev["frame"] / 30
        destino = SAIDA / f"cesta_{n:02d}_t{int(INICIO + segundo)}s.mp4"
        inicio_clipe = max(0, segundo - CONTEXTO)
        print(f"  {n:2d}. frame {ev['frame']:>5} "
              f"(~{int(INICIO + segundo)//60}min{int(INICIO + segundo)%60:02d}s)"
              f" -> {destino.name}")
        recortar(clipe, destino, inicio_clipe, CONTEXTO * 2, recodificar=True)

    print(f"\n  clipes em {SAIDA}")
    print("  assista e classifique: os erros alimentam a anotação (04_falhas/)")

    clipe.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
