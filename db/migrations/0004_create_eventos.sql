-- Eventos são a fonte da verdade de tudo que acontece numa partida: cestas
-- de 2 ou 3 pontos, lances livres e faltas. O placar da partida e a súmula
-- são sempre calculados a partir daqui — nunca guardados de forma solta em
-- outra tabela, para não correr o risco de placar e eventos ficarem
-- inconsistentes entre si.
CREATE TABLE eventos (
    id SERIAL PRIMARY KEY,
    partida_id INTEGER NOT NULL REFERENCES partidas(id) ON DELETE CASCADE,
    jogador_id INTEGER NOT NULL REFERENCES jogadores(id),
    tipo VARCHAR(20) NOT NULL
        CHECK (tipo IN ('cesta_2', 'cesta_3', 'lance_livre', 'falta')),
    pontos SMALLINT NOT NULL DEFAULT 0,
    -- Posição no vídeo de origem (em milissegundos) onde o evento ocorreu,
    -- para permitir revisão/auditoria da detecção automática mais adiante.
    tempo_video_ms INTEGER,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Garante, no próprio banco, que a pontuação bate com o tipo do evento
    -- (regra de negócio das Regras IA.md: 2pts, 3pts, 1pt de lance livre e
    -- falta sem pontos diretos).
    CHECK (
        (tipo = 'cesta_2'    AND pontos = 2) OR
        (tipo = 'cesta_3'    AND pontos = 3) OR
        (tipo = 'lance_livre' AND pontos = 1) OR
        (tipo = 'falta'      AND pontos = 0)
    )
);

CREATE INDEX idx_eventos_partida ON eventos(partida_id);
CREATE INDEX idx_eventos_jogador ON eventos(jogador_id);
