#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera pré-anotações para importar no CVAT, usando o nosso modelo.

Por que não usar a auto-anotação do próprio CVAT: ela exige subir o Nuclio e
compilar cada função serverless, e o único detector genérico disponível
(YOLOv7/COCO) conhece `person` e `sports ball` — mas **não conhece `basket`**.
Seria muito trabalho de infraestrutura para ainda ter que marcar o aro à mão.

Nosso modelo já conhece as três classes. Rodar aqui e importar o resultado
dá pré-anotação melhor, sem infraestrutura nenhuma.

Uso:
    python pre_anotar.py ../revisao/04_falhas/fp_01_t3692s.mp4
    python pre_anotar.py <video> --saida /tmp/anotacoes.xml
"""

import sys
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ_IA = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_IA))

from deteccao import CONF, IMGSZ, eh_falso_positivo  # noqa: E402

PESOS = RAIZ_IA / "outputs" / "treino" / "bola_aro_v1" / "weights" / "best.pt"


def _iou(a: tuple, b: tuple) -> float:
    """Sobreposição entre duas caixas, de 0 a 1."""
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return 0.0
    inter = (x2 - x1) * (y2 - y1)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (area_a + area_b - inter)


def montar_tracks(por_frame: dict[int, list[tuple]],
                  iou_min: float = 0.3) -> list[dict[int, tuple]]:
    """Liga caixas de frames vizinhos em tracks, casando pela sobreposição.

    Sem isso, cada detecção viraria uma caixa solta e o CVAT não ofereceria
    interpolação — que é justamente o que torna a correção rápida. O
    casamento é guloso e simples: para cada track aberto, procura no frame
    seguinte a caixa que mais se sobrepõe a ele.
    """
    tracks: list[dict[int, tuple]] = []
    abertos: list[int] = []          # índices em `tracks` ainda ativos

    for frame in sorted(por_frame):
        disponiveis = list(por_frame[frame])
        ainda_abertos = []

        for idx in abertos:
            ultimo = tracks[idx][max(tracks[idx])]
            melhor, melhor_iou = None, iou_min
            for caixa in disponiveis:
                s = _iou(ultimo, caixa)
                if s >= melhor_iou:
                    melhor, melhor_iou = caixa, s
            if melhor is not None:
                tracks[idx][frame] = melhor
                disponiveis.remove(melhor)
                ainda_abertos.append(idx)
            # Sem correspondência: o track termina aqui.

        # O que sobrou são objetos novos.
        for caixa in disponiveis:
            tracks.append({frame: caixa})
            ainda_abertos.append(len(tracks) - 1)

        abertos = ainda_abertos

    return tracks


def coletar(video: str) -> tuple[dict[str, dict[int, list[tuple]]], int]:
    """Detecta em todos os frames. Devolve {classe: {frame: [caixas]}}."""
    from ultralytics import YOLO

    modelo = YOLO(str(PESOS))
    por_classe: dict[str, dict[int, list[tuple]]] = {}
    total = 0

    for n, r in enumerate(modelo.predict(video, conf=CONF, imgsz=IMGSZ,
                                         verbose=False, stream=True)):
        total = n + 1
        altura = r.orig_shape[0]
        for i, cls in enumerate(r.boxes.cls):
            nome = modelo.names[int(cls)]
            x1, y1, x2, y2 = (float(v) for v in r.boxes.xyxy[i])
            if eh_falso_positivo(nome, (y1 + y2) / 2, altura):
                continue
            # TODAS as caixas, não só a de maior confiança. Exportar uma
            # pessoa por frame, quando há oito em quadra, transformaria as
            # outras sete em "fundo" no treino — ensinando o modelo a não
            # detectar pessoas.
            por_classe.setdefault(nome, {}).setdefault(n, []).append((x1, y1, x2, y2))

    return por_classe, total


def gerar_xml(por_classe: dict[str, dict[int, list[tuple]]], total: int) -> str:
    """Monta o XML no formato 'CVAT for video 1.1'.

    Cada sequência contínua de detecções vira um `track`. Usar tracks (e não
    shapes soltas) é o que permite editar com interpolação dentro do CVAT —
    justamente o recurso que torna a correção rápida.
    """
    linhas = ['<?xml version="1.0" encoding="utf-8"?>', "<annotations>",
              "  <version>1.1</version>"]
    id_track = 0

    for classe, por_frame in sorted(por_classe.items()):
        for track in montar_tracks(por_frame):
            linhas.append(f'  <track id="{id_track}" label="{escape(classe)}" source="manual">')
            for f in sorted(track):
                x1, y1, x2, y2 = track[f]
                linhas.append(
                    f'    <box frame="{f}" outside="0" occluded="0" keyframe="1"'
                    f' xtl="{x1:.2f}" ytl="{y1:.2f}" xbr="{x2:.2f}" ybr="{y2:.2f}"'
                    f' z_order="0"></box>'
                )
            # O CVAT precisa de um box "outside" para saber onde o track acaba.
            fim = max(track) + 1
            if fim < total:
                x1, y1, x2, y2 = track[max(track)]
                linhas.append(
                    f'    <box frame="{fim}" outside="1" occluded="0" keyframe="1"'
                    f' xtl="{x1:.2f}" ytl="{y1:.2f}" xbr="{x2:.2f}" ybr="{y2:.2f}"'
                    f' z_order="0"></box>'
                )
            linhas.append("  </track>")
            id_track += 1

    linhas.append("</annotations>")
    return "\n".join(linhas)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__, file=sys.stderr)
        return 1

    video = Path(args[0])
    if not video.exists():
        print(f"vídeo não encontrado: {video}", file=sys.stderr)
        return 1
    if not PESOS.exists():
        print(f"pesos não encontrados: {PESOS}", file=sys.stderr)
        return 1

    saida = Path(sys.argv[sys.argv.index("--saida") + 1]) if "--saida" in sys.argv \
        else video.with_suffix(".cvat.xml")

    print(f"detectando em {video.name} (imgsz={IMGSZ})…")
    por_classe, total = coletar(str(video))

    if not por_classe:
        print("nenhuma detecção — nada a exportar", file=sys.stderr)
        return 1

    saida.write_text(gerar_xml(por_classe, total), encoding="utf-8")

    print(f"\n  {total} frames")
    for classe, por_frame in sorted(por_classe.items()):
        caixas = sum(len(v) for v in por_frame.values())
        print(f"    {classe:<8} em {len(por_frame):>4} frames ({100*len(por_frame)/total:>3.0f}%)"
              f"  ·  {caixas} caixas")
    print(f"\n  arquivo: {saida}")
    print("\n  No CVAT: abra a tarefa -> menu ⋮ -> Upload annotations")
    print("           -> formato 'CVAT for video 1.1' -> selecione esse .xml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
