import { useState } from "react";
import type { Jogador, LinhaSumula, Partida, Time, TipoEvento } from "../api";
import { api } from "../api";

type Props = {
  partida: Partida;
  times: Time[];
  jogadores: Jogador[];
  sumula: LinhaSumula[];
  aoRegistrar: () => void;
  aoErrar: (mensagem: string) => void;
};

const ACOES: { tipo: TipoEvento; rotulo: string }[] = [
  { tipo: "cesta_2", rotulo: "+2" },
  { tipo: "cesta_3", rotulo: "+3" },
  { tipo: "lance_livre", rotulo: "+1" },
  { tipo: "falta", rotulo: "Falta" },
];

export function PainelPlacar({
  partida,
  times,
  jogadores,
  sumula,
  aoRegistrar,
  aoErrar,
}: Props) {
  const [enviando, setEnviando] = useState<string | null>(null);

  const nomeTime = (id: number) => times.find((t) => t.id === id)?.nome ?? `#${id}`;

  // O placar do time é a soma da súmula dos seus jogadores — a mesma regra
  // do backend: nada de placar guardado separado dos eventos.
  const pontosDoTime = (timeId: number) =>
    sumula.filter((l) => l.time_id === timeId).reduce((s, l) => s + l.pontos_totais, 0);

  async function registrar(jogadorId: number, tipo: TipoEvento) {
    const chave = `${jogadorId}-${tipo}`;
    setEnviando(chave);
    try {
      await api.registrarEvento(partida.id, jogadorId, tipo);
      aoRegistrar();
    } catch (erro) {
      aoErrar((erro as Error).message);
    } finally {
      setEnviando(null);
    }
  }

  const jogadoresDoTime = (timeId: number) =>
    jogadores.filter((j) => j.time_id === timeId);

  const semJogadores =
    jogadoresDoTime(partida.time_casa_id).length === 0 &&
    jogadoresDoTime(partida.time_visitante_id).length === 0;

  return (
    <>
      <section className="cartao">
        <h2>
          Placar — {nomeTime(partida.time_casa_id)} × {nomeTime(partida.time_visitante_id)}
        </h2>

        <div className="placar-times">
          <div className="placar-time">
            <div className="nome">{nomeTime(partida.time_casa_id)}</div>
            <div className="pontos">{pontosDoTime(partida.time_casa_id)}</div>
          </div>
          <div className="placar-x">×</div>
          <div className="placar-time">
            <div className="nome">{nomeTime(partida.time_visitante_id)}</div>
            <div className="pontos">{pontosDoTime(partida.time_visitante_id)}</div>
          </div>
        </div>

        {semJogadores && (
          <p className="vazio">
            Os times desta partida não têm jogadores cadastrados. Cadastre-os ao lado
            para registrar eventos.
          </p>
        )}

        {[partida.time_casa_id, partida.time_visitante_id].map((timeId) => {
          const doTime = jogadoresDoTime(timeId);
          if (doTime.length === 0) return null;

          return (
            <div key={timeId} style={{ marginTop: 14 }}>
              <h3 style={{ fontSize: "0.9rem", marginBottom: 4 }}>{nomeTime(timeId)}</h3>
              {doTime.map((j) => (
                <div className="jogador-linha" key={j.id}>
                  {j.numero_camisa !== null && (
                    <span className="camisa">{j.numero_camisa}</span>
                  )}
                  <span className="jogador-nome">{j.nome}</span>
                  <div className="botoes-evento">
                    {ACOES.map(({ tipo, rotulo }) => (
                      <button
                        key={tipo}
                        onClick={() => registrar(j.id, tipo)}
                        disabled={enviando !== null}
                      >
                        {enviando === `${j.id}-${tipo}` ? "…" : rotulo}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          );
        })}
      </section>

      <section className="cartao">
        <h2>Súmula</h2>
        {sumula.length === 0 ? (
          <p className="vazio">Nenhum evento registrado ainda.</p>
        ) : (
          <div className="tabela-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Jogador</th>
                  <th>Time</th>
                  <th className="numero">Pontos</th>
                  <th className="numero">Faltas</th>
                </tr>
              </thead>
              <tbody>
                {sumula.map((l) => (
                  <tr key={l.jogador_id}>
                    <td>{l.jogador_nome}</td>
                    <td className="vazio">{l.time_nome}</td>
                    <td className="numero total">{l.pontos_totais}</td>
                    <td className="numero">{l.faltas}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
