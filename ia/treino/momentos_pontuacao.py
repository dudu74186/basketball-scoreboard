#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Encontra no vídeo os instantes em que o placar mudou.

Serve de **verdade de referência**: com a lista de quando pontos foram
marcados, dá para medir o recall do detector de cestas por número, em vez de
por inferência, e para escolher com precisão quais trechos anotar.

## Como funciona, e por que não é OCR

Tentamos OCR (EasyOCR) e ele errou 5 de 6 leituras — a fonte de placar
eletrônico é muito diferente do que esses modelos aprendem. Também tentamos
diferença de pixels no recorte largo do placar, e o fundo (quadra, logos)
gerava ruído maior que o sinal.

O que funciona: recortar **só os dígitos, dentro da barra preta**, binarizar
pelo brilho e comparar as máscaras entre amostras. Medido num trecho de
placar estável, o ruído tem mediana 30 e p90 89, contra 800–1100 de uma
mudança real. A separação é limpa.

Note que não lemos o VALOR do placar — só detectamos que ele mudou. Para o
objetivo (achar os momentos e conferir no vídeo) isso basta, e é bem mais
robusto que tentar reconhecer os dígitos.

Uso:
    INICIO=3600 DURACAO=1200 python momentos_pontuacao.py
"""

import os
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

RAIZ_IA = Path(__file__).resolve().parent.parent
VIDEO = os.environ.get("VIDEO_SOURCE", str(RAIZ_IA / "samples" / "circuito_capixaba_final_bronze.mp4"))
INICIO = int(os.environ.get("INICIO", "3600"))
DURACAO = int(os.environ.get("DURACAO", "1200"))
SAIDA = RAIZ_IA / "revisao" / "05_pontuacao"

# Recortes dos dígitos de cada placar, em fração do quadro. Precisam ficar
# DENTRO da barra preta: incluir a quadra ou os logos ao redor multiplica o
# ruído por dez (medido).
REGIOES = {
    "casa": (0.362, 0.410, 0.880, 0.936),
    "visitante": (0.606, 0.654, 0.880, 0.936),
}

LIMIAR_BRILHO = int(os.environ.get("LIMIAR_BRILHO", "200"))
LIMIAR_MUDANCA = int(os.environ.get("LIMIAR_MUDANCA", "400"))
PASSO = int(os.environ.get("PASSO", "15"))          # 0,5s a 30fps

# Uma mudança de placar leva alguns quadros para ser redesenhada; sem isso,
# o mesmo evento apareceria repetido.
INTERVALO_MINIMO = int(os.environ.get("INTERVALO_MINIMO", "5"))

# Amostras consecutivas que a mudança precisa persistir para ser aceita.
#
# É o filtro que separa sinal de ruído aqui. O placar só muda para valores
# que FICAM: uma vez que sobe, continua diferente do que era. Já o ruído
# (um jogador de branco passando atrás da barra semitransparente, um corte
# de câmera) é transitório — no instante seguinte a máscara volta ao que
# era. Sem esta exigência, uma varredura de 20 minutos acusou 60 eventos
# para 16 pontos realmente marcados.
PERSISTENCIA = int(os.environ.get("PERSISTENCIA", "4"))

# Segundos antes da mudança que o clipe deve cobrir. O placar sobe DEPOIS da
# cesta, com o atraso da reação do mesário — a jogada está para trás.
ANTES = float(os.environ.get("ANTES", "8"))
DEPOIS = float(os.environ.get("DEPOIS", "2"))

NUCLEO = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))


def mascara(frame, regiao, altura, largura):
    x1, x2, y1, y2 = regiao
    corte = frame[int(altura * y1):int(altura * y2), int(largura * x1):int(largura * x2)]
    cinza = cv2.cvtColor(corte, cv2.COLOR_BGR2GRAY)
    binaria = (cinza > LIMIAR_BRILHO).astype(np.uint8)
    # A abertura remove respingos isolados de compressão, que sozinhos já
    # somariam algumas dezenas de pixels de diferença.
    return cv2.morphologyEx(binaria, cv2.MORPH_OPEN, NUCLEO)


def main() -> int:
    if not Path(VIDEO).exists():
        print(f"vídeo não encontrado: {VIDEO}", file=sys.stderr)
        return 1

    SAIDA.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(VIDEO)
    largura, altura = int(cap.get(3)), int(cap.get(4))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30

    print(f"varrendo {INICIO}s a {INICIO+DURACAO}s (amostra a cada {PASSO/fps:.1f}s)…")

    # `referencia` é a máscara do último estado ESTÁVEL do placar — só é
    # atualizada quando uma mudança se confirma. Comparar sempre contra ela
    # (e não contra a amostra anterior) é o que permite exigir persistência.
    referencia: dict[str, np.ndarray] = {}
    pendente: dict[str, list] = {}          # lado -> [segundo, dif, contagem]
    eventos: list[tuple[float, str, int]] = []
    ultimo = -999.0

    frame_n = int(INICIO * fps)
    fim = int((INICIO + DURACAO) * fps)
    while frame_n < fim:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_n)
        ok, frame = cap.read()
        if not ok:
            break
        segundo = frame_n / fps

        for lado, regiao in REGIOES.items():
            atual = mascara(frame, regiao, altura, largura)

            if lado not in referencia:
                referencia[lado] = atual
                continue

            dif = int(np.abs(atual.astype(int) - referencia[lado].astype(int)).sum())

            if dif <= LIMIAR_MUDANCA:
                # Voltou ao estado anterior: era ruído passageiro.
                pendente.pop(lado, None)
                continue

            if lado not in pendente:
                pendente[lado] = [segundo, dif, 1]
            else:
                pendente[lado][2] += 1
                pendente[lado][1] = max(pendente[lado][1], dif)

            if pendente[lado][2] >= PERSISTENCIA:
                inicio_mudanca, maior_dif, _ = pendente.pop(lado)
                if inicio_mudanca - ultimo >= INTERVALO_MINIMO:
                    eventos.append((inicio_mudanca, lado, maior_dif))
                    ultimo = inicio_mudanca
                # Novo estado estável.
                referencia[lado] = atual

        frame_n += PASSO

    cap.release()

    if not eventos:
        print("nenhuma mudança de placar detectada")
        return 0

    print(f"\n  {len(eventos)} mudanças de placar:\n")
    for n, (segundo, lado, dif) in enumerate(eventos, 1):
        print(f"   {n:2d}. {int(segundo)//60}min{int(segundo)%60:02d}s"
              f"  ({lado}, delta={dif})")

    print(f"\n  gerando clipes em {SAIDA}…")
    for n, (segundo, lado, _) in enumerate(eventos, 1):
        destino = SAIDA / f"pt_{n:02d}_{int(segundo)//60}min{int(segundo)%60:02d}s_{lado}.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-ss", str(max(0, segundo - ANTES)), "-i", VIDEO,
             "-t", str(ANTES + DEPOIS),
             "-c:v", "libx264", "-crf", "23", "-preset", "fast",
             "-vf", "scale=1280:-2", str(destino)],
            capture_output=True,
        )

    print(f"  {len(eventos)} clipes. Cada um termina logo após o placar subir —")
    print("  a jogada está nos segundos anteriores.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
