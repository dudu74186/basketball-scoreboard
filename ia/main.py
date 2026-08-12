#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 21 22:53:49 2026

@author: eduardo
"""

#%%

import os

from ultralytics import YOLO

# Configuração via variáveis de ambiente, com os valores de antes como padrão
# para quem já usava o script localmente sem setar nada. Isso deixa o script
# portável entre execução local, container Docker e (futuramente) Windows.
MODEL_PATH = os.environ.get("MODEL_PATH", "models/yolo11n.pt")
VIDEO_SOURCE = os.environ.get("VIDEO_SOURCE", "samples/teste.mp4")
SHOW_VIDEO = os.environ.get("SHOW_VIDEO", "true").lower() == "true"

# Resolvido para caminho absoluto de propósito: o ultralytics, quando recebe
# um "project" relativo, prefixa por conta própria com o runs_dir/task
# internos dele (ex.: vira ".../runs/detect/outputs/runs/detect/predict"),
# o que bagunça a pasta de saída e, dentro de um container, escreve fora do
# volume montado. Passando já absoluto, ele usa o caminho como está.
OUTPUT_DIR = os.path.abspath(os.environ.get("OUTPUT_DIR", "outputs/runs/detect"))

# Carrega o modelo
model = YOLO(MODEL_PATH)

# Cria o gerador de inferência
results = model(
    VIDEO_SOURCE, show=SHOW_VIDEO, save=True, stream=True, project=OUTPUT_DIR
)

# O LOOP FOR É O QUE FAZ O VÍDEO RODAR DE FATO:
for r in results:
    pass  # O 'pass' serve apenas para manter o loop rodando frame por frame
