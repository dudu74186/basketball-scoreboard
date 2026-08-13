-- A súmula não vira uma tabela própria — seria dado duplicado (o mesmo
-- placar guardado em dois lugares corre o risco de ficar dessincronizado).
-- Em vez disso, é uma VIEW: cada consulta recalcula os totais a partir dos
-- eventos, então ela nunca pode "ficar desatualizada".
CREATE VIEW vw_sumula AS
SELECT
    p.id AS partida_id,
    j.id AS jogador_id,
    j.nome AS jogador_nome,
    j.time_id,
    t.nome AS time_nome,
    COALESCE(SUM(e.pontos), 0) AS pontos_totais,
    COUNT(*) FILTER (WHERE e.tipo = 'falta') AS faltas
FROM partidas p
JOIN jogadores j ON j.time_id IN (p.time_casa_id, p.time_visitante_id)
JOIN times t ON t.id = j.time_id
LEFT JOIN eventos e ON e.partida_id = p.id AND e.jogador_id = j.id
GROUP BY p.id, j.id, j.nome, j.time_id, t.nome;
