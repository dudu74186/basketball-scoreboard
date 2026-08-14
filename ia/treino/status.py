#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resumo do treino em andamento (ou do último que rodou).

Uso:
    python status.py
    NOME_RUN=outro_treino python status.py
"""

import csv
import os
import subprocess
from datetime import timedelta
from pathlib import Path

RAIZ_IA = Path(__file__).resolve().parent.parent
NOME_RUN = os.environ.get("NOME_RUN", "bola_aro_v1")
PASTA = RAIZ_IA / "outputs" / "treino" / NOME_RUN
EPOCAS_ALVO = int(os.environ.get("EPOCAS", "60"))


def processo_rodando() -> str | None:
    """PID do treino, se houver.

    O filtro por 'python' evita o falso positivo clássico: o próprio pgrep
    (e o shell que o invoca) tem 'treinar.py' na linha de comando e casaria
    consigo mesmo.
    """
    try:
        saida = subprocess.run(
            ["pgrep", "-af", "treinar.py"], capture_output=True, text=True
        ).stdout
    except FileNotFoundError:
        return None

    for linha in saida.splitlines():
        pid, _, cmd = linha.partition(" ")
        if cmd.startswith("python") or "/python" in cmd.split()[0]:
            return pid
    return None


def barra(fracao: float, largura: int = 28) -> str:
    cheios = int(fracao * largura)
    return "█" * cheios + "░" * (largura - cheios)


def main() -> int:
    print(f"\n  treino: {NOME_RUN}")

    pid = processo_rodando()
    print(f"  estado: {'RODANDO (pid ' + pid + ')' if pid else 'parado'}")

    csv_path = PASTA / "results.csv"
    if not csv_path.exists():
        print(f"\n  ainda sem results.csv em {PASTA}")
        print("  (a primeira época ainda não terminou)\n")
        return 0

    with csv_path.open() as f:
        linhas = [l for l in csv.DictReader(f) if l.get("epoch")]

    if not linhas:
        print("\n  results.csv vazio — primeira época em andamento\n")
        return 0

    col = {c.strip(): c for c in linhas[0]}
    feitas = len(linhas)
    ultima = linhas[-1]

    def valor(nome: str) -> float:
        return float(ultima[col[nome]])

    fracao = feitas / EPOCAS_ALVO
    print(f"\n  {barra(fracao)}  {feitas}/{EPOCAS_ALVO} épocas ({fracao:.0%})")

    # A coluna 'time' é o tempo acumulado desde o início, em segundos.
    decorrido = float(ultima[col["time"]])
    por_epoca = decorrido / feitas
    restante = (EPOCAS_ALVO - feitas) * por_epoca
    print(f"  {timedelta(seconds=int(decorrido))} decorridos"
          f"  ·  ~{por_epoca / 60:.1f} min/época"
          f"  ·  faltam ~{timedelta(seconds=int(restante))}")

    print("\n  métricas da última época:")
    for rotulo, chave in [
        ("precisão", "metrics/precision(B)"),
        ("recall", "metrics/recall(B)"),
        ("mAP50", "metrics/mAP50(B)"),
        ("mAP50-95", "metrics/mAP50-95(B)"),
    ]:
        print(f"    {rotulo:<10} {valor(chave):.3f}")

    # Evolução: o que interessa é se ainda está subindo. Se estagnou, o
    # early stopping vai encerrar sozinho — e não adianta esperar mais.
    mapa = col["metrics/mAP50(B)"]
    print("\n  evolução do mAP50:")
    passo = max(1, feitas // 6)
    for l in linhas[::passo]:
        e = int(float(l[col["epoch"]]))
        print(f"    época {e:>2}: {float(l[mapa]):.3f}")
    if feitas > 1:
        delta = float(linhas[-1][mapa]) - float(linhas[-2][mapa])
        print(f"    (última variação: {delta:+.3f})")

    pesos = PASTA / "weights" / "best.pt"
    if pesos.exists():
        print(f"\n  melhores pesos: {pesos}")
        print("  (atualizados a cada época — já dá para avaliar sem esperar o fim)")

    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
