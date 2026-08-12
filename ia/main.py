#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 21 22:53:49 2026

@author: eduardo
"""

#%%

from ultralytics import YOLO

# Carrega o modelo
model = YOLO("yolo11n.pt")

# Cria o gerador de inferência
results = model("/home/eduardo/Documentos/Python/COMETAS X CESB - RODADA 16 - LCB 2021.mp4", show=True, save=True, stream=True)

# O LOOP FOR É O QUE FAZ O VÍDEO RODAR DE FATO:
for r in results:
    pass  # O 'pass' serve apenas para manter o loop rodando frame por frame
