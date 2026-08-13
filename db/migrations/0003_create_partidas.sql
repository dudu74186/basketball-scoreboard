-- Partidas entre dois times, com modalidade (3x3 ou 5x5) e status de andamento.
CREATE TABLE partidas (
    id SERIAL PRIMARY KEY,
    modalidade VARCHAR(3) NOT NULL CHECK (modalidade IN ('3x3', '5x5')),
    time_casa_id INTEGER NOT NULL REFERENCES times(id),
    time_visitante_id INTEGER NOT NULL REFERENCES times(id),
    data_hora TIMESTAMPTZ NOT NULL DEFAULT now(),
    status VARCHAR(20) NOT NULL DEFAULT 'agendada'
        CHECK (status IN ('agendada', 'em_andamento', 'finalizada')),
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Um time não pode jogar contra si mesmo.
    CHECK (time_casa_id <> time_visitante_id)
);
