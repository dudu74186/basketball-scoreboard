#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mede a cobertura da bola NOS ARREMESSOS, não na média do jogo.

A pergunta que isso responde: o detector perde as cestas porque não vê a
bola no momento do arremesso, ou porque a lógica descarta o que ele viu?

A cobertura média (64%) mistura longos trechos de bola quicando no meio da
quadra — situação fácil — com os segundos do arremesso, que são o que
importa. Se a cobertura despencar nesses segundos, o gargalo está na
detecção; se ficar alta, está na lógica de cesta.

Os instantes vêm da verdade de referência classificada por humano em
`verdade_60_80min.py`. Como o placar sobe DEPOIS da jogada, a janela olha
para trás a partir da mudança.

Uso:
    python cobertura_arremessos.py
"""

import os
import subprocess
import sys
from pathlib import Path

RAIZ_IA = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_IA))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from deteccao import CONF, IMGSZ, eh_falso_positivo  # noqa: E402
from verdade_60_80min import EVENTOS  # noqa: E402

PESOS = os.environ.get(
    "PESOS", str(RAIZ_IA / "outputs" / "treino" / "bola_aro_v2" / "weights" / "best.pt")
)
VIDEO = os.environ.get("VIDEO_SOURCE", str(RAIZ_IA / "samples" / "circuito_capixaba_final_bronze.mp4"))

# Segundos antes da mudança de placar que a janela cobre. O arremesso
# acontece nesse intervalo: a bola sobe, entra, e só então o mesário reage.
ANTES = float(os.environ.get("ANTES", "8"))

# Baseline já medido na janela inteira de 60–80min, para comparação.
COBERTURA_GERAL = 64


def analisar(modelo, clipe: str) -> tuple[int, int, int]:
    """Devolve (frames, frames com bola, frames com aro)."""
    total = com_bola = com_aro = 0
    for r in modelo.predict(clipe, conf=CONF, imgsz=IMGSZ, verbose=False, stream=True):
        total += 1
        altura = r.orig_shape[0]
        bola = aro = False
        for cls, caixa in zip(r.boxes.cls, r.boxes.xywh):
            nome = modelo.names[int(cls)]
            if nome == "ball" and not eh_falso_positivo("ball", float(caixa[1]), altura):
                bola = True
            elif nome == "basket":
                aro = True
        com_bola += bola
        com_aro += aro
    return total, com_bola, com_aro


def main() -> int:
    for caminho, nome in ((PESOS, "pesos"), (VIDEO, "vídeo")):
        if not Path(caminho).exists():
            print(f"{nome} não encontrado: {caminho}", file=sys.stderr)
            return 1

    reais = [e for e in EVENTOS if e[2] != "nenhum"]
    print(f"\n  {len(reais)} pontuações reais  ·  janela de {ANTES:.0f}s antes de cada")
    print(f"  pesos: {Path(PESOS).parent.parent.name}\n")

    from ultralytics import YOLO

    modelo = YOLO(PESOS)
    tmp = RAIZ_IA / "outputs" / "_cobertura.mp4"

    print(f"  {'evento':<22}{'bola':>8}{'aro':>8}")
    print("  " + "-" * 38)

    soma_frames = soma_bola = soma_aro = 0
    por_tipo: dict[str, list[float]] = {}

    for n, segundo, tipo, _ in reais:
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(max(0, segundo - ANTES)),
             "-i", VIDEO, "-t", str(ANTES), "-c", "copy", str(tmp)],
            capture_output=True,
        )
        total, bola, aro = analisar(modelo, str(tmp))
        if total == 0:
            continue

        pct_bola = 100 * bola / total
        soma_frames += total
        soma_bola += bola
        soma_aro += aro
        por_tipo.setdefault(tipo, []).append(pct_bola)

        rotulo = f"{n:>2}. {segundo//60}min{segundo%60:02d}s {tipo[:11]}"
        print(f"  {rotulo:<22}{pct_bola:>7.0f}%{100*aro/total:>7.0f}%")

    tmp.unlink(missing_ok=True)

    if not soma_frames:
        print("nada analisado", file=sys.stderr)
        return 1

    geral = 100 * soma_bola / soma_frames
    print("  " + "-" * 38)
    print(f"  {'MÉDIA nos arremessos':<22}{geral:>7.0f}%{100*soma_aro/soma_frames:>7.0f}%")
    print(f"  {'média do jogo todo':<22}{COBERTURA_GERAL:>7}%")

    print("\n  por tipo de jogada:")
    for tipo, valores in sorted(por_tipo.items()):
        print(f"    {tipo:<14} {sum(valores)/len(valores):>5.0f}%   ({len(valores)} eventos)")

    print("\n  Como ler:")
    print("    cobertura nos arremessos MENOR que a geral -> o gargalo é a")
    print("      detecção da bola, e anotar esses trechos é o caminho.")
    print("    cobertura parecida ou maior -> o modelo vê a bola, e quem")
    print("      descarta é a lógica de cesta em ia/cestas.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
