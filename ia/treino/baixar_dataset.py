#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baixa do Roboflow Universe o dataset público que serve de base do treino.

Estratégia híbrida (decidida em 14/08/2026): treinar primeiro com dado
público, ver onde o modelo erra nos vídeos reais e só então anotar os casos
difíceis — em vez de anotar milhares de frames às cegas.

Uso:
    pip install -r requirements.txt
    export ROBOFLOW_API_KEY=...        # ou coloque no ia/.env
    python baixar_dataset.py
"""

import os
import sys
from pathlib import Path

from _ambiente import carregar_env

# Carrega ia/.env antes de qualquer os.environ.get abaixo.
carregar_env()

# Onde o dataset é gravado. Fica fora do Git (ver .gitignore): são milhares
# de imagens, e qualquer um pode rebaixá-las com este script.
DESTINO = Path(__file__).resolve().parent.parent / "datasets"

# Dataset padrão. Trocar por outro é só ajustar estas variáveis de ambiente
# — o endereço de qualquer dataset do Universe segue o mesmo formato:
#   https://universe.roboflow.com/<WORKSPACE>/<PROJETO>/dataset/<VERSAO>
WORKSPACE = os.environ.get("RF_WORKSPACE", "computer-vision-d5fjh")
PROJETO = os.environ.get("RF_PROJETO", "basketball-detection-dn6fg")
# v4 é a maior deste projeto: 7.486 imagens (6.017 de treino), contra apenas
# 499 da v1. Um projeto do Roboflow costuma ter várias versões, e a página
# do Universe mostra o total do projeto, não o de cada versão — vale sempre
# conferir antes de baixar. Para listar as versões disponíveis:
#     p = rf.workspace(WORKSPACE).project(PROJETO)
#     for v in p.versions(): print(v.id, v.images)
VERSAO = int(os.environ.get("RF_VERSAO", "4"))

# "yolov11" entrega o formato que o ultralytics espera: imagens + labels em
# .txt normalizados, já divididos em train/valid/test, com um data.yaml.
FORMATO = os.environ.get("RF_FORMATO", "yolov11")


def main() -> int:
    chave = os.environ.get("ROBOFLOW_API_KEY")
    if not chave:
        print(
            "ROBOFLOW_API_KEY não definida.\n\n"
            "  1. Crie uma conta gratuita em https://roboflow.com\n"
            "  2. Pegue a chave em Settings → API Keys\n"
            "  3. Coloque em ia/.env:  ROBOFLOW_API_KEY=sua-chave\n"
            "     (o .env não é versionado)\n",
            file=sys.stderr,
        )
        return 1

    try:
        from roboflow import Roboflow
    except ImportError:
        print(
            "pacote 'roboflow' não instalado.\n"
            "  pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1

    DESTINO.mkdir(parents=True, exist_ok=True)

    print(f"baixando {WORKSPACE}/{PROJETO} v{VERSAO} ({FORMATO}) em {DESTINO}…")

    rf = Roboflow(api_key=chave)
    projeto = rf.workspace(WORKSPACE).project(PROJETO)
    dataset = projeto.version(VERSAO).download(FORMATO, location=str(DESTINO / PROJETO))

    print(f"\npronto: {dataset.location}")
    print("confira o data.yaml gerado — é ele que o treinar.py consome.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
