# -*- coding: utf-8 -*-
"""Configuração e pós-processamento das detecções.

Fica na raiz de `ia/` (e não em `treino/`) porque tanto a avaliação quanto o
serviço de inferência precisam aplicar exatamente as mesmas regras — se cada
um filtrasse do seu jeito, o que você mede na avaliação não seria o que roda
em produção.
"""

import os

# Resolução de inferência. Medida no vídeo real (640x360, câmera distante):
#
#   imgsz | % frames c/ bola | % frames c/ aro | aros por frame
#     640 |            4,0%  |          90,7%  |  1,00
#     960 |            5,2%  |          92,7%  |  1,76  <- duplicando o aro
#    1280 |            6,3%  |          91,8%  |  1,03
#
# 1280 detecta ~58% mais bola que 640, sem introduzir duplicatas, ao custo
# de ~2x no tempo. Vale: a bola é o gargalo, e o processamento é offline.
# Note que 1280 é MAIOR que o vídeo (640x360): o upscale dá mais pixels ao
# objeto pequeno, e é justamente isso que ajuda o modelo a enxergar a bola.
IMGSZ = int(os.environ.get("IMGSZ", "1280"))

CONF = float(os.environ.get("CONF", "0.25"))

# Fração da altura, a partir do topo, onde ficam os placares sobrepostos ao
# vídeo. O modelo confunde o gráfico do placar com a bola: 67,6% de todas as
# detecções de bola no jogo inteiro caíam nessa faixa. Como a bola real
# praticamente nunca aparece no topo do quadro numa filmagem de quadra,
# descartar essa região elimina o falso positivo sem custo.
# Use 0 para desligar (ex.: vídeo sem overlay).
FAIXA_PLACAR = float(os.environ.get("FAIXA_PLACAR", "0.15"))


def eh_falso_positivo(nome_classe: str, centro_y: float, altura: int) -> bool:
    """Diz se uma detecção deve ser descartada.

    Por ora só trata o caso do placar. Outras regras (ex.: aro fora da
    região da quadra) entram aqui conforme forem sendo identificadas.
    """
    if FAIXA_PLACAR <= 0:
        return False
    return nome_classe == "ball" and centro_y < altura * FAIXA_PLACAR


def filtrar(resultado, nomes: dict) -> list[tuple[str, float]]:
    """Devolve [(classe, confiança)] das detecções que sobreviveram ao filtro."""
    altura = resultado.orig_shape[0]
    mantidas = []
    for cls, caixa, conf in zip(
        resultado.boxes.cls, resultado.boxes.xywh, resultado.boxes.conf
    ):
        nome = nomes[int(cls)]
        if eh_falso_positivo(nome, float(caixa[1]), altura):
            continue
        mantidas.append((nome, float(conf)))
    return mantidas
