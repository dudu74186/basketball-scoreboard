# -*- coding: utf-8 -*-
"""Trajetória da bola ao longo do tempo.

A detecção quadro a quadro produz pontos soltos: a bola some quando fica
borrada, tapada por um jogador ou pequena demais. Para decidir se houve
cesta é preciso uma *trajetória* contínua, não detecções isoladas.

**Interpolação de lacunas** resolve isso: se a bola aparece no frame 10 e
some até o 14, a posição entre eles é preenchida por interpolação linear. Só
vale para lacunas curtas — em 30fps, 15 frames são meio segundo, tempo em que
a bola realmente pode ter mudado de direção.

## Por que NÃO usamos ByteTrack aqui

A intuição dizia que um rastreador ajudaria. A medição disse o contrário
(60s do vídeo de referência, 1801 frames):

    detecção pura                     571 frames (31,7%)   seq. máx 5,0s
    + ByteTrack                       493 frames (27,4%)   seq. máx 5,0s
    + ByteTrack + interpolação        679 frames (37,7%)   seq. máx 7,1s
    detecção pura + interpolação      841 frames (46,7%)   seq. máx 7,1s  <=

O rastreador **piorou** a cobertura (-14%). O motivo: o ByteTrack só emite
um track depois de confirmá-lo em alguns frames seguidos, e descarta
detecções isoladas. Para uma bola que aparece de forma esporádica, esse é
exatamente o comportamento errado — ele joga fora justamente o que temos.

Ele também trocou de ID 20 vezes em 60 segundos, o que quebraria qualquer
trajetória construída a partir dos IDs.

Conclusão: a interpolação é que dá o ganho (+47% sobre a detecção pura), e
ela não precisa de rastreador. Reavaliar se um dia a detecção da bola ficar
consistente — aí o ByteTrack teria material para trabalhar.
"""

import os

# Lacuna máxima (em frames) que aceitamos preencher por interpolação.
# Acima disso, é mais honesto assumir que perdemos a bola do que inventar
# uma trajetória que pode não ter acontecido.
LACUNA_MAX = int(os.environ.get("LACUNA_MAX", "15"))

# Velocidade máxima plausível da bola, em pixels por frame (a 1080p).
# Serve de teste de sanidade: se duas detecções exigem que a bola tenha
# atravessado a quadra num piscar, quase certamente NÃO são a mesma bola —
# é o modelo detectando objetos diferentes, e interpolar entre eles fabrica
# uma trajetória que nunca existiu (foi assim que um falso positivo de cesta
# apareceu: uma reta da mão do jogador até o aro, cruzando a linha).
VELOCIDADE_MAX = float(os.environ.get("VELOCIDADE_MAX", "60"))

# Mantido só para o script de comparação poder reproduzir a medição acima.
# Não é usado no caminho normal — ver a explicação no topo do arquivo.
RASTREADOR = os.environ.get("RASTREADOR", "bytetrack.yaml")


def interpolar_lacunas(posicoes: dict[int, tuple[float, float]],
                       lacuna_max: int = LACUNA_MAX) -> dict[int, tuple[float, float]]:
    """Preenche buracos curtos entre posições conhecidas.

    `posicoes` mapeia número do frame -> (x, y) do centro da bola.
    Devolve um novo dicionário com os frames interpolados incluídos.
    """
    if not posicoes:
        return {}

    frames = sorted(posicoes)
    completo = dict(posicoes)

    for anterior, seguinte in zip(frames, frames[1:]):
        salto = seguinte - anterior
        if salto <= 1 or salto > lacuna_max:
            continue

        (x0, y0), (x1, y1) = posicoes[anterior], posicoes[seguinte]

        # Teste de velocidade: distância percorrida por frame precisa ser
        # plausível. Caso contrário são duas bolas diferentes, e ligar as
        # duas com uma reta inventa movimento que não houve.
        distancia = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        if distancia / salto > VELOCIDADE_MAX:
            continue
        for passo in range(1, salto):
            fracao = passo / salto
            completo[anterior + passo] = (
                x0 + (x1 - x0) * fracao,
                y0 + (y1 - y0) * fracao,
            )

    return completo


def maior_sequencia(frames: set[int]) -> int:
    """Maior quantidade de frames consecutivos presentes no conjunto.

    Serve de medida de continuidade: uma trajetória útil para detectar
    cesta precisa de vários frames seguidos, não de pontos espalhados.
    """
    if not frames:
        return 0

    ordenados = sorted(frames)
    melhor = atual = 1
    for anterior, seguinte in zip(ordenados, ordenados[1:]):
        atual = atual + 1 if seguinte == anterior + 1 else 1
        melhor = max(melhor, atual)
    return melhor
