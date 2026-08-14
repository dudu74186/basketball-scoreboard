#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resumo do treino em andamento (ou do último que rodou).

Uso:
    python status.py              # imprime uma vez
    python status.py -w           # fica atualizando até o treino acabar
    python status.py -w -n 10     # atualizando a cada 10s
    python status.py --linha      # uma linha só (para tmux/polybar/watch)

    NOME_RUN=outro_treino python status.py
"""

import csv
import os
import subprocess
import sys
import time
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
        if not cmd:
            continue
        if cmd.startswith("python") or "/python" in cmd.split()[0]:
            return pid
    return None


def ler_epocas() -> list[dict]:
    csv_path = PASTA / "results.csv"
    if not csv_path.exists():
        return []
    try:
        with csv_path.open() as f:
            return [l for l in csv.DictReader(f) if l.get("epoch")]
    except (OSError, csv.Error):
        # O treino reescreve o arquivo a cada época; se cair exatamente no
        # meio de uma escrita, é melhor pular esta atualização do que morrer.
        return []


def barra(fracao: float, largura: int = 28) -> str:
    cheios = int(fracao * largura)
    return "█" * cheios + "░" * (largura - cheios)


def montar_painel(linhas: list[dict], pid: str | None) -> str:
    saida = [f"\n  treino: {NOME_RUN}"]
    saida.append(f"  estado: {'RODANDO (pid ' + pid + ')' if pid else 'parado'}")

    if not linhas:
        saida.append(f"\n  ainda sem results.csv em {PASTA}")
        saida.append("  (a primeira época ainda não terminou)\n")
        return "\n".join(saida)

    col = {c.strip(): c for c in linhas[0]}
    feitas = len(linhas)
    ultima = linhas[-1]
    fracao = feitas / EPOCAS_ALVO

    saida.append(f"\n  {barra(fracao)}  {feitas}/{EPOCAS_ALVO} épocas ({fracao:.0%})")

    # A coluna 'time' é o tempo acumulado desde o início, em segundos.
    decorrido = float(ultima[col["time"]])
    por_epoca = decorrido / feitas
    restante = (EPOCAS_ALVO - feitas) * por_epoca
    saida.append(
        f"  {timedelta(seconds=int(decorrido))} decorridos"
        f"  ·  ~{por_epoca / 60:.1f} min/época"
        f"  ·  faltam ~{timedelta(seconds=int(restante))}"
    )

    saida.append("\n  métricas da última época:")
    for rotulo, chave in [
        ("precisão", "metrics/precision(B)"),
        ("recall", "metrics/recall(B)"),
        ("mAP50", "metrics/mAP50(B)"),
        ("mAP50-95", "metrics/mAP50-95(B)"),
    ]:
        saida.append(f"    {rotulo:<10} {float(ultima[col[chave]]):.3f}")

    # Evolução: o que interessa é se ainda está subindo. Se estagnou, o
    # early stopping vai encerrar sozinho — e não adianta esperar mais.
    mapa = col["metrics/mAP50(B)"]
    saida.append("\n  evolução do mAP50:")
    passo = max(1, feitas // 6)
    for l in linhas[::passo]:
        e = int(float(l[col["epoch"]]))
        saida.append(f"    época {e:>2}: {float(l[mapa]):.3f}")
    if feitas > 1:
        delta = float(linhas[-1][mapa]) - float(linhas[-2][mapa])
        saida.append(f"    (última variação: {delta:+.3f})")

    pesos = PASTA / "weights" / "best.pt"
    if pesos.exists():
        saida.append(f"\n  melhores pesos: {pesos}")
        saida.append("  (atualizados a cada época — já dá para avaliar sem esperar o fim)")

    return "\n".join(saida) + "\n"


def montar_linha(linhas: list[dict], pid: str | None) -> str:
    """Versão de uma linha, para barra de status (tmux, polybar, i3blocks)."""
    if not linhas:
        return f"🏀 {NOME_RUN}: iniciando…"

    col = {c.strip(): c for c in linhas[0]}
    feitas = len(linhas)
    ultima = linhas[-1]
    mapa = float(ultima[col["metrics/mAP50(B)"]])

    decorrido = float(ultima[col["time"]])
    restante = (EPOCAS_ALVO - feitas) * (decorrido / feitas)
    falta = f"{timedelta(seconds=int(restante))}" if pid else "parado"

    return f"🏀 {feitas}/{EPOCAS_ALVO} · mAP50 {mapa:.3f} · {falta}"


def main() -> int:
    args = sys.argv[1:]
    modo_linha = "--linha" in args
    observar = "-w" in args or "--watch" in args

    intervalo = 15
    if "-n" in args:
        intervalo = int(args[args.index("-n") + 1])

    if not observar:
        linhas = ler_epocas()
        pid = processo_rodando()
        print(montar_linha(linhas, pid) if modo_linha else montar_painel(linhas, pid))
        return 0

    try:
        while True:
            linhas = ler_epocas()
            pid = processo_rodando()

            if modo_linha:
                # \r volta ao início da linha e reescreve por cima: assim a
                # barra de status não vira um histórico rolando a tela.
                print(f"\r{montar_linha(linhas, pid)}   ", end="", flush=True)
            else:
                # Limpa a tela e volta o cursor ao topo, redesenhando o
                # painel inteiro no lugar em vez de empilhar.
                print("\033[2J\033[H", end="")
                print(montar_painel(linhas, pid))
                # flush explícito: fora de um terminal o Python bufferiza a
                # saída, e quem redirecionar para arquivo (ou matar o
                # processo) não veria nada.
                print(f"  atualizando a cada {intervalo}s — Ctrl+C para sair", flush=True)

            terminou = pid is None and len(linhas) > 0
            if terminou:
                print("\n  treino finalizado.")
                return 0

            time.sleep(intervalo)
    except KeyboardInterrupt:
        # Sair do monitor não afeta o treino, que roda em outro processo.
        print("\n  (monitor encerrado; o treino continua rodando)")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
