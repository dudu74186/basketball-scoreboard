-- Jogadores, vinculados a um time. Um jogador pertence a um único time por
-- enquanto (simplificação inicial: liga informal, não temporadas/transferências).
CREATE TABLE jogadores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    numero_camisa SMALLINT,
    time_id INTEGER NOT NULL REFERENCES times(id) ON DELETE CASCADE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Dois jogadores do mesmo time não podem usar o mesmo número de camisa.
    UNIQUE (time_id, numero_camisa)
);
