#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cliente gRPC para reportar à API os eventos detectados pela visão computacional.

Este módulo é a ponte entre o serviço de IA (Python) e o backend (Rust).
O contrato das mensagens está em proto/placar.proto — mudou lá, rode
./gerar_stubs.sh para regenerar os stubs deste lado.
"""

import os

import grpc

from .gerado import placar_pb2, placar_pb2_grpc

# Nome do serviço no docker-compose quando roda containerizado; localhost
# quando roda direto na máquina.
GRPC_ADDR = os.environ.get("GRPC_ADDR", "localhost:50051")

# Nomes amigáveis -> constantes do protobuf. Deixa quem chama escrever
# "cesta_3" em vez de importar o enum gerado.
TIPOS = {
    "cesta_2": placar_pb2.CESTA_2,
    "cesta_3": placar_pb2.CESTA_3,
    "lance_livre": placar_pb2.LANCE_LIVRE,
    "falta": placar_pb2.FALTA,
}


class ClientePlacar:
    """Conexão com a API. Use como context manager para fechar o canal."""

    def __init__(self, endereco=None):
        self.canal = grpc.insecure_channel(endereco or GRPC_ADDR)
        self.stub = placar_pb2_grpc.PlacarStub(self.canal)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.fechar()

    def fechar(self):
        self.canal.close()

    @staticmethod
    def _montar(partida_id, jogador_id, tipo, tempo_video_ms=None):
        if tipo not in TIPOS:
            raise ValueError(f"tipo inválido: {tipo!r}; use um de {sorted(TIPOS)}")

        return placar_pb2.EventoDetectado(
            partida_id=partida_id,
            jogador_id=jogador_id,
            tipo=TIPOS[tipo],
            tempo_video_ms=tempo_video_ms,
        )

    def registrar(self, partida_id, jogador_id, tipo, tempo_video_ms=None):
        """Registra um evento e espera a confirmação.

        Note que não se envia a pontuação: quem decide quantos pontos vale
        cada tipo é o servidor.
        """
        evento = self._montar(partida_id, jogador_id, tipo, tempo_video_ms)
        return self.stub.RegistrarEvento(evento)

    def registrar_lote(self, eventos):
        """Envia vários eventos por uma única conexão e recebe um resumo.

        `eventos` é um iterável de tuplas
        (partida_id, jogador_id, tipo, tempo_video_ms) — pode ser um gerador,
        que é o caso interessante: dá para ir enviando as detecções enquanto
        o vídeo ainda está sendo processado, sem acumular tudo em memória.
        """
        fluxo = (self._montar(*ev) for ev in eventos)
        return self.stub.RegistrarEventos(fluxo)
