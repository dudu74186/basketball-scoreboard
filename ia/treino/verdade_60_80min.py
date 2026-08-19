#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verdade de referência da janela 60–80min, classificada por humano.

Os 19 clipes de `ia/revisao/05_pontuacao/` (momentos em que o placar mudou)
foram assistidos e classificados pelo usuário em 16/08/2026. Este arquivo
guarda esse julgamento para que a avaliação do detector seja reproduzível —
sem precisar reassistir tudo a cada nova versão do modelo.

Uso:
    python verdade_60_80min.py                # mostra o resumo
    python verdade_60_80min.py --comparar     # cruza com os candidatos
"""

import sys

# (nº do clipe, segundo absoluto no vídeo, tipo, pontos)
#
# "nenhum" = o detector de placar acusou mudança, mas não houve pontuação.
# São falsos positivos DELE, não do detector de cestas.
EVENTOS = [
    (1,  3700, "cesta",       2),
    (2,  3719, "lance_livre", 1),
    (3,  3814, "lance_livre", 1),
    (4,  3845, "nenhum",      0),
    (5,  3851, "nenhum",      0),
    (6,  3858, "nenhum",      0),
    # A bola bateu no aro mas não entrou — exatamente o caso ambíguo em 2D.
    (7,  3942, "nenhum",      0),
    (8,  4019, "lance_livre", 1),
    (9,  4195, "cesta",       2),   # pontuação não anotada; assumido 2
    (10, 4200, "cesta",       2),
    (11, 4218, "nenhum",      0),
    (12, 4225, "nenhum",      0),
    (13, 4230, "nenhum",      0),
    (14, 4237, "nenhum",      0),
    # Tocou a rede mas passou por fora do aro.
    (15, 4244, "nenhum",      0),
    (16, 4274, "cesta",       2),
    (17, 4315, "cesta",       2),
    (18, 4522, "lance_livre", 1),
    (19, 4583, "nenhum",      0),
]

# Candidatos do detector de cestas rodando com os pesos v2, mesma janela.
CANDIDATOS_V2 = [3692, 3765, 3919, 4117, 4312, 4464, 4609, 4751]

# Quanto tempo o mesário leva para atualizar o placar depois da jogada.
# Um candidato casa com um evento se a mudança de placar vier nessa janela
# depois dele.
ATRASO_MIN, ATRASO_MAX = -3, 20


def reais():
    return [e for e in EVENTOS if e[2] != "nenhum"]


def resumo():
    r = reais()
    cestas = [e for e in r if e[2] == "cesta"]
    lances = [e for e in r if e[2] == "lance_livre"]
    pontos = sum(e[3] for e in r)

    print(f"\n  19 mudanças de placar detectadas, classificadas por humano:\n")
    print(f"    pontuações reais ...... {len(r)}")
    print(f"      cestas de quadra .... {len(cestas)}")
    print(f"      lances livres ....... {len(lances)}")
    print(f"    falsos positivos ...... {len(EVENTOS)-len(r)}")
    print(f"\n    precisão do detector de PLACAR: {100*len(r)/len(EVENTOS):.0f}%")
    print(f"    pontos somados: {pontos}  (placar mediu +16 na janela)")
    if pontos != 16:
        print(f"    ⚠ diferença de {16-pontos} ponto(s): o detector de placar")
        print("      provavelmente perdeu alguma mudança")


def comparar():
    r = reais()
    casados_cand, casados_ev = set(), set()

    for c in CANDIDATOS_V2:
        for n, seg, tipo, _ in r:
            if ATRASO_MIN <= seg - c <= ATRASO_MAX:
                casados_cand.add(c)
                casados_ev.add(n)
                break

    cestas = [e for e in r if e[2] == "cesta"]
    cestas_pegas = [e for e in cestas if e[0] in casados_ev]

    print(f"\n  Detector de cestas (v2) vs verdade:\n")
    print(f"    candidatos ............ {len(CANDIDATOS_V2)}")
    print(f"    acertos ............... {len(casados_cand)}")
    print(f"    falsos positivos ...... {len(CANDIDATOS_V2)-len(casados_cand)}")
    print(f"\n    PRECISÃO .............. {100*len(casados_cand)/len(CANDIDATOS_V2):.0f}%")
    print(f"    RECALL (tudo) ......... {100*len(casados_ev)/len(r):.0f}%"
          f"   ({len(casados_ev)}/{len(r)})")
    print(f"    RECALL (só cestas) .... {100*len(cestas_pegas)/len(cestas):.0f}%"
          f"   ({len(cestas_pegas)}/{len(cestas)})")

    print("\n    pontuações NÃO detectadas:")
    for n, seg, tipo, pts in r:
        if n not in casados_ev:
            print(f"      clipe {n:>2}  {seg//60}min{seg%60:02d}s  {tipo} ({pts}pt)")

    print("\n    candidatos SEM pontuação correspondente:")
    for c in CANDIDATOS_V2:
        if c not in casados_cand:
            print(f"      {c//60}min{c%60:02d}s")


if __name__ == "__main__":
    resumo()
    if "--comparar" in sys.argv:
        comparar()
