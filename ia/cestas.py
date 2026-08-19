# -*- coding: utf-8 -*-
"""Decide, a partir da trajetória, quando houve uma cesta.

Aqui não há IA: é lógica temporal sobre as posições que a detecção produziu.
A regra central é simples de enunciar — *a bola cruzou a linha do aro, de
cima para baixo, dentro da largura do aro* — e cheia de armadilhas na
prática.

## O que esta abordagem NÃO consegue distinguir

O vídeo é uma projeção 2D. Uma bola passando **na frente** (ou atrás) do aro
desenha exatamente o mesmo movimento de uma bola entrando nele. Sem
profundidade, essa ambiguidade é irredutível — nenhum ajuste de parâmetro
resolve.

Por isso o objetivo aqui não é acertar 100%, e sim gerar **candidatos** com
poucos falsos negativos, para conferência humana na tela de revisão. Errar
para mais (marcar cesta que não houve) é preferível a errar para menos:
descartar um candidato errado custa um clique, descobrir uma cesta perdida
custa rever o jogo inteiro.

Mitigações já aplicadas, todas ajustáveis:
- exigir que a bola esteja acima do aro por alguns frames antes, e abaixo
  por alguns frames depois — filtra ruído de detecção isolada;
- exigir passagem dentro de uma fração da largura do aro (o `basket` do
  modelo costuma englobar a tabela, bem mais larga que o cesto);
- tempo mínimo entre eventos, para o mesmo arremesso não contar duas vezes.
"""

import os
from statistics import median

# Fração da largura da caixa do aro que conta como "passou por dentro".
#
# Começou em 0.45, pensando que a caixa incluiria a tabela. Medindo no vídeo
# real, a caixa do aro tem só ~65px a 1080p, então 0.45 dava um portão de
# **30 pixels** — e uma cesta confirmada foi rejeitada por 10px de folga.
# Como a posição da bola é o centro de uma caixa detectada, com tremida de
# vários pixels, 10px está dentro do erro da própria medição: estávamos
# descartando cesta por ruído.
#
# 0.8 é uma troca deliberada: aumenta o falso positivo, mas o gargalo hoje é
# o recall (22%), não a precisão. Revisar quando o recall subir.
LARGURA_UTIL = float(os.environ.get("LARGURA_UTIL", "0.8"))

# Onde, dentro da caixa do aro, fica a linha do cesto (0 = topo, 1 = base).
# A tabela ocupa a parte de cima, então o aro fica na metade inferior.
ALTURA_LINHA = float(os.environ.get("ALTURA_LINHA", "0.65"))

# Frames que a bola precisa passar acima da linha antes, e abaixo depois.
# Sobe esses números para reduzir falso positivo; desce para não perder
# arremessos rápidos.
FRAMES_ACIMA = int(os.environ.get("FRAMES_ACIMA", "3"))
FRAMES_ABAIXO = int(os.environ.get("FRAMES_ABAIXO", "3"))

# Intervalo mínimo entre duas cestas (em frames). A 30fps, 90 = 3 segundos.
INTERVALO_MINIMO = int(os.environ.get("INTERVALO_MINIMO", "90"))

# Quantos dos frames ao redor do cruzamento precisam ser detecção REAL, e
# não interpolação. Um cruzamento sustentado apenas por pontos inventados
# não é evidência de nada: foi exatamente assim que uma reta traçada da mão
# do jogador até o aro virou "cesta". Zero desliga a exigência.
MIN_REAIS = int(os.environ.get("MIN_REAIS", "3"))


def estabilizar_aro(aros: dict[int, tuple[int, int, int, int]],
                    total_frames: int,
                    janela: int = 150) -> dict[int, tuple[int, int, int, int]]:
    """Preenche as lacunas na posição do aro ao longo do vídeo.

    O aro é detectado de forma intermitente, mas é uma estrutura fixa: entre
    duas detecções, ele só se move se a câmera se mover.

    **A versão anterior usava a mediana de uma janela para TODO frame,
    inclusive os que tinham detecção própria — e isso era um defeito real:**
    a mediana depende de quais frames caem na janela, então a posição
    calculada mudava conforme o tamanho do trecho analisado. Uma cesta
    detectada num recorte de 5 minutos podia sumir ao rodar 20 minutos, com
    o mesmo vídeo e o mesmo modelo. Resultado dependente do tamanho do lote
    é o tipo de comportamento que torna qualquer medição não confiável.

    Agora:
    - frame COM detecção usa a própria, que é a informação mais fiel àquele
      instante (importa quando a câmera acompanha a jogada);
    - frame SEM detecção interpola entre a detecção anterior e a seguinte,
      o que é determinístico e não depende do tamanho da janela.

    O parâmetro `janela` é mantido só por compatibilidade e não é mais usado.
    """
    if not aros:
        return {}

    conhecidos = sorted(aros)
    estabilizado = {}

    for frame in range(total_frames):
        if frame in aros:
            estabilizado[frame] = aros[frame]
            continue

        anteriores = [f for f in conhecidos if f < frame]
        seguintes = [f for f in conhecidos if f > frame]

        if anteriores and seguintes:
            a, b = anteriores[-1], seguintes[0]
            fracao = (frame - a) / (b - a)
            estabilizado[frame] = tuple(
                int(aros[a][i] + (aros[b][i] - aros[a][i]) * fracao) for i in range(4)
            )
        else:
            # Antes da primeira ou depois da última: repete a mais próxima.
            vizinho = (anteriores or seguintes)[-1 if anteriores else 0]
            estabilizado[frame] = aros[vizinho]

    return estabilizado


def _linha_e_portao(caixa: tuple[int, int, int, int]) -> tuple[float, float, float]:
    """Da caixa do aro, extrai (altura da linha, x mínimo, x máximo)."""
    x1, y1, x2, y2 = caixa
    linha_y = y1 + (y2 - y1) * ALTURA_LINHA
    centro_x = (x1 + x2) / 2
    meia_largura = (x2 - x1) * LARGURA_UTIL / 2
    return linha_y, centro_x - meia_largura, centro_x + meia_largura


def detectar_cestas(trajetoria: dict[int, tuple[float, float]],
                    aros: dict[int, tuple[int, int, int, int]],
                    reais: set[int] | None = None) -> list[dict]:
    """Encontra os frames em que a bola cruzou o aro de cima para baixo.

    `trajetoria` mapeia frame -> (x, y) do centro da bola (já interpolada).
    `aros` mapeia frame -> caixa do aro (já estabilizada).
    `reais` são os frames com detecção de verdade (não interpolada). Se
    informado, exige-se que o cruzamento aconteça perto de detecção real —
    ver `MIN_REAIS`.

    Devolve uma lista de eventos com o frame do cruzamento e o contexto que
    permitiu a decisão — útil para depurar e para recortar o trecho depois.
    """
    if not trajetoria or not aros:
        return []

    frames = sorted(trajetoria)
    eventos: list[dict] = []
    ultimo_evento = -INTERVALO_MINIMO

    for i, frame in enumerate(frames):
        if frame - ultimo_evento < INTERVALO_MINIMO:
            continue
        if frame not in aros:
            continue

        linha_y, x_min, x_max = _linha_e_portao(aros[frame])
        _, y = trajetoria[frame]

        # A bola precisa estar abaixo da linha AGORA...
        if y <= linha_y:
            continue

        # ...e ter estado acima nos frames anteriores.
        anteriores = frames[max(0, i - FRAMES_ACIMA):i]
        if len(anteriores) < FRAMES_ACIMA:
            continue
        if not all(trajetoria[f][1] < linha_y for f in anteriores):
            continue

        # ...e continuar abaixo nos seguintes (descarta a bola que só
        # tangenciou a linha e voltou a subir — típico de rebote no aro).
        seguintes = frames[i + 1:i + 1 + FRAMES_ABAIXO]
        if len(seguintes) < FRAMES_ABAIXO:
            continue
        if not all(trajetoria[f][1] > linha_y for f in seguintes):
            continue

        # E a passagem tem que ser dentro da largura útil do aro.
        x_cruzamento = trajetoria[frame][0]
        if not (x_min <= x_cruzamento <= x_max):
            continue

        # O cruzamento precisa se apoiar em detecção real, não só em pontos
        # interpolados. Sem isso, uma reta traçada entre duas detecções
        # distantes atravessa a linha e vira "cesta" do nada.
        if reais is not None and MIN_REAIS > 0:
            vizinhos = anteriores + [frame] + seguintes
            if sum(1 for f in vizinhos if f in reais) < MIN_REAIS:
                continue

        eventos.append({
            "frame": frame,
            "x": x_cruzamento,
            "y": y,
            "linha_y": linha_y,
            "aro": aros[frame],
        })
        ultimo_evento = frame

    return eventos
