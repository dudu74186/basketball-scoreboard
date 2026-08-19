#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Descobre QUAL critério da lógica de cesta rejeitou uma pontuação real.

A medição de cobertura mostrou que alguns eventos perdidos tinham bola
visível em ~78% dos frames e o aro visível o tempo todo — ou seja, o dado
estava lá e a lógica descartou. Este script refaz o caminho de decisão frame
a frame e diz onde cada candidato morreu.

Sem isso, "a lógica está rígida" é palpite; com isso, sabe-se exatamente
qual parâmetro afrouxar (e o quanto).

Uso:
    python diagnosticar_perdidas.py            # os eventos perdidos
    EVENTOS=9,10,16 python diagnosticar_perdidas.py
"""

import os
import subprocess
import sys
from pathlib import Path

RAIZ_IA = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_IA))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import cestas  # noqa: E402
from deteccao import CONF, IMGSZ, eh_falso_positivo  # noqa: E402
from rastreamento import interpolar_lacunas  # noqa: E402
from verdade_60_80min import EVENTOS  # noqa: E402

PESOS = os.environ.get(
    "PESOS", str(RAIZ_IA / "outputs" / "treino" / "bola_aro_v2" / "weights" / "best.pt")
)
VIDEO = os.environ.get("VIDEO_SOURCE", str(RAIZ_IA / "samples" / "circuito_capixaba_final_bronze.mp4"))
JANELA = float(os.environ.get("JANELA", "10"))     # segundos antes do placar subir

ALVOS = [int(x) for x in os.environ["EVENTOS"].split(",")] if os.environ.get("EVENTOS") \
    else [9, 10, 16]


def coletar(modelo, clipe):
    bola, aros, total = {}, {}, 0
    for n, r in enumerate(modelo.predict(clipe, conf=CONF, imgsz=IMGSZ,
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
    return bola, aros, total


def diagnosticar(trajetoria, aros, reais):
    """Repete a lógica de cestas.py contando onde cada frame foi barrado."""
    frames = sorted(trajetoria)
    motivos = {
        "sem aro no frame": 0,
        "bola não está abaixo da linha": 0,
        "faltam frames antes": 0,
        "bola não estava acima antes": 0,
        "faltam frames depois": 0,
        "bola não seguiu abaixo": 0,
        "fora da largura do aro": 0,
        "poucas detecções reais": 0,
        "ACEITO": 0,
    }
    quase = []          # frames que passaram do cruzamento vertical

    for i, frame in enumerate(frames):
        if frame not in aros:
            motivos["sem aro no frame"] += 1
            continue

        linha_y, x_min, x_max = cestas._linha_e_portao(aros[frame])
        _, y = trajetoria[frame]

        if y <= linha_y:
            motivos["bola não está abaixo da linha"] += 1
            continue

        anteriores = frames[max(0, i - cestas.FRAMES_ACIMA):i]
        if len(anteriores) < cestas.FRAMES_ACIMA:
            motivos["faltam frames antes"] += 1
            continue
        if not all(trajetoria[f][1] < linha_y for f in anteriores):
            motivos["bola não estava acima antes"] += 1
            continue

        seguintes = frames[i + 1:i + 1 + cestas.FRAMES_ABAIXO]
        if len(seguintes) < cestas.FRAMES_ABAIXO:
            motivos["faltam frames depois"] += 1
            continue
        if not all(trajetoria[f][1] > linha_y for f in seguintes):
            motivos["bola não seguiu abaixo"] += 1
            continue

        # Daqui em diante, o cruzamento vertical ACONTECEU. O que barrar
        # agora é critério de posição horizontal ou de qualidade do dado —
        # e é onde vale olhar de perto.
        x = trajetoria[frame][0]
        folga = min(abs(x - x_min), abs(x - x_max))
        if not (x_min <= x <= x_max):
            motivos["fora da largura do aro"] += 1
            quase.append((frame, "fora da largura", x, x_min, x_max, folga))
            continue

        vizinhos = anteriores + [frame] + seguintes
        n_reais = sum(1 for f in vizinhos if f in reais)
        if n_reais < cestas.MIN_REAIS:
            motivos["poucas detecções reais"] += 1
            quase.append((frame, f"só {n_reais} detecções reais", x, x_min, x_max, 0))
            continue

        motivos["ACEITO"] += 1
        quase.append((frame, "ACEITO", x, x_min, x_max, 0))

    return motivos, quase


def main() -> int:
    alvos = [e for e in EVENTOS if e[0] in ALVOS]
    if not alvos:
        print("nenhum evento correspondente", file=sys.stderr)
        return 1

    from ultralytics import YOLO
    modelo = YOLO(PESOS)
    tmp = RAIZ_IA / "outputs" / "_diag.mp4"

    print(f"\n  parâmetros atuais: FRAMES_ACIMA={cestas.FRAMES_ACIMA}"
          f"  FRAMES_ABAIXO={cestas.FRAMES_ABAIXO}"
          f"  LARGURA_UTIL={cestas.LARGURA_UTIL}"
          f"  ALTURA_LINHA={cestas.ALTURA_LINHA}"
          f"  MIN_REAIS={cestas.MIN_REAIS}")

    for n, segundo, tipo, _ in alvos:
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(max(0, segundo - JANELA)),
             "-i", VIDEO, "-t", str(JANELA + 2), "-c", "copy", str(tmp)],
            capture_output=True,
        )
        bola, aros, total = coletar(modelo, str(tmp))
        trajetoria = interpolar_lacunas(bola)
        aros_est = cestas.estabilizar_aro(aros, total) if aros else {}

        print(f"\n  ── evento {n}: {segundo//60}min{segundo%60:02d}s ({tipo}) "
              f"— {total} frames, bola em {len(trajetoria)}")

        if not aros_est:
            print("     aro nunca detectado neste trecho")
            continue

        motivos, quase = diagnosticar(trajetoria, aros_est, set(bola))
        for motivo, n_frames in motivos.items():
            if n_frames:
                print(f"     {motivo:<32} {n_frames:>4} frames")

        if quase:
            print("     frames que cruzaram a linha na vertical:")
            for f, razao, x, xi, xf, folga in quase[:6]:
                extra = f"  (x={x:.0f}, portão {xi:.0f}–{xf:.0f}, faltou {folga:.0f}px)" \
                    if "largura" in razao else ""
                print(f"       frame {f:>4}: {razao}{extra}")

    tmp.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
