#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta um dataset YOLO a partir de um export do CVAT + o vídeo de origem.

Por que existe: é fácil exportar do CVAT sem marcar *Save images* e receber
um zip só com os `.txt` de label. Como o vídeo original está aqui, os frames
podem ser extraídos localmente — não é preciso refazer a exportação.

Uso:
    python importar_cvat.py "../datasets/Video 1.zip" ../revisao/04_falhas/fp_01_t3692s.mp4 clipe1
"""

import sys
import zipfile
from pathlib import Path

RAIZ_IA = Path(__file__).resolve().parent.parent
DESTINO_BASE = RAIZ_IA / "datasets" / "proprio"


def main() -> int:
    if len(sys.argv) < 4:
        print(__doc__, file=sys.stderr)
        return 1

    zip_path, video_path, nome = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]

    for caminho in (zip_path, video_path):
        if not caminho.exists():
            print(f"não encontrado: {caminho}", file=sys.stderr)
            return 1

    destino = DESTINO_BASE / nome
    imagens = destino / "train" / "images"
    labels = destino / "train" / "labels"
    imagens.mkdir(parents=True, exist_ok=True)
    labels.mkdir(parents=True, exist_ok=True)

    # --- labels ---
    classes: list[str] = []
    with zipfile.ZipFile(zip_path) as z:
        if "obj.names" in z.namelist():
            classes = z.read("obj.names").decode().split()

        nomes_txt = [n for n in z.namelist() if n.endswith(".txt")
                     and "obj_train_data" in n and "frame_" in n]
        for interno in nomes_txt:
            (labels / Path(interno).name).write_bytes(z.read(interno))

    if not classes:
        print("obj.names ausente no zip — não dá para saber a ordem das classes",
              file=sys.stderr)
        return 1

    print(f"  classes: {classes}")
    print(f"  {len(nomes_txt)} arquivos de label")

    # --- imagens ---
    import cv2

    cap = cv2.VideoCapture(str(video_path))
    salvas = 0
    n = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        # O nome precisa casar com o do label: o YOLO pareia imagem e rótulo
        # pelo nome do arquivo, ignorando a extensão.
        alvo = labels / f"frame_{n:06d}.txt"
        if alvo.exists():
            cv2.imwrite(str(imagens / f"frame_{n:06d}.jpg"), frame,
                        [cv2.IMWRITE_JPEG_QUALITY, 95])
            salvas += 1
        n += 1
    cap.release()

    print(f"  {salvas} imagens extraídas de {video_path.name}")

    orfas = len(nomes_txt) - salvas
    if orfas > 0:
        print(f"  ⚠ {orfas} labels sem imagem correspondente — o vídeo tem "
              f"menos frames que o export", file=sys.stderr)

    # --- data.yaml ---
    (destino / "data.yaml").write_text(
        f"train: {(destino / 'train' / 'images').resolve()}\n"
        f"nc: {len(classes)}\n"
        f"names: {classes}\n",
        encoding="utf-8",
    )

    print(f"  pronto: {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
