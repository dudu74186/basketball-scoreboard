import { useState } from "react";
import type { Partida, Time } from "../api";
import { api } from "../api";

type Props = {
  times: Time[];
  partidas: Partida[];
  partidaAtiva: number | null;
  aoSelecionar: (id: number) => void;
  aoMudar: () => void;
  aoErrar: (mensagem: string) => void;
};

export function PainelPartidas({
  times,
  partidas,
  partidaAtiva,
  aoSelecionar,
  aoMudar,
  aoErrar,
}: Props) {
  const [modalidade, setModalidade] = useState("5x5");
  const [casa, setCasa] = useState("");
  const [visitante, setVisitante] = useState("");
  const [salvando, setSalvando] = useState(false);

  const nomeTime = (id: number) => times.find((t) => t.id === id)?.nome ?? `#${id}`;

  async function criar(e: React.FormEvent) {
    e.preventDefault();
    setSalvando(true);
    try {
      const nova = await api.criarPartida({
        modalidade,
        time_casa_id: Number(casa),
        time_visitante_id: Number(visitante),
      });
      aoMudar();
      // Já entra na partida recém-criada: é quase sempre o que se quer.
      aoSelecionar(nova.id);
    } catch (erro) {
      aoErrar((erro as Error).message);
    } finally {
      setSalvando(false);
    }
  }

  // O backend rejeita time jogando contra si mesmo (CHECK no banco), mas
  // bloquear aqui também evita uma ida ao servidor só para receber erro.
  const mesmoTime = casa !== "" && casa === visitante;

  return (
    <section className="cartao">
      <h2>Partidas</h2>

      <form onSubmit={criar}>
        <div className="linha-form">
          <select value={modalidade} onChange={(e) => setModalidade(e.target.value)}>
            <option value="5x5">5x5</option>
            <option value="3x3">3x3</option>
          </select>
        </div>
        <div className="linha-form">
          <select value={casa} onChange={(e) => setCasa(e.target.value)}>
            <option value="">Casa…</option>
            {times.map((t) => (
              <option key={t.id} value={t.id}>
                {t.nome}
              </option>
            ))}
          </select>
          <select value={visitante} onChange={(e) => setVisitante(e.target.value)}>
            <option value="">Visitante…</option>
            {times.map((t) => (
              <option key={t.id} value={t.id}>
                {t.nome}
              </option>
            ))}
          </select>
        </div>
        <div className="linha-form">
          <button
            className="primario"
            disabled={salvando || !casa || !visitante || mesmoTime}
          >
            Criar partida
          </button>
        </div>
        {mesmoTime && <p className="vazio">Um time não pode jogar contra si mesmo.</p>}
      </form>

      {partidas.length === 0 ? (
        <p className="vazio">Nenhuma partida criada.</p>
      ) : (
        <ul className="lista">
          {partidas.map((p) => (
            <li key={p.id}>
              <span>
                {nomeTime(p.time_casa_id)} × {nomeTime(p.time_visitante_id)}{" "}
                <span className="vazio">({p.modalidade})</span>
              </span>
              <button
                onClick={() => aoSelecionar(p.id)}
                disabled={partidaAtiva === p.id}
              >
                {partidaAtiva === p.id ? "aberta" : "abrir"}
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
