import { useState } from "react";
import type { Jogador, Time } from "../api";
import { api } from "../api";

type Props = {
  times: Time[];
  jogadores: Jogador[];
  aoMudar: () => void;
  aoErrar: (mensagem: string) => void;
};

/** Cadastro de times e jogadores — o que antes era feito por curl. */
export function PainelCadastro({ times, jogadores, aoMudar, aoErrar }: Props) {
  const [nomeTime, setNomeTime] = useState("");
  const [nomeJogador, setNomeJogador] = useState("");
  const [camisa, setCamisa] = useState("");
  const [timeDoJogador, setTimeDoJogador] = useState("");
  const [salvando, setSalvando] = useState(false);

  async function criarTime(e: React.FormEvent) {
    e.preventDefault();
    if (!nomeTime.trim()) return;
    setSalvando(true);
    try {
      await api.criarTime(nomeTime.trim());
      setNomeTime("");
      aoMudar();
    } catch (erro) {
      aoErrar((erro as Error).message);
    } finally {
      setSalvando(false);
    }
  }

  async function criarJogador(e: React.FormEvent) {
    e.preventDefault();
    if (!nomeJogador.trim() || !timeDoJogador) return;
    setSalvando(true);
    try {
      await api.criarJogador({
        nome: nomeJogador.trim(),
        // Camisa é opcional: campo vazio vira null, não 0.
        numero_camisa: camisa === "" ? null : Number(camisa),
        time_id: Number(timeDoJogador),
      });
      setNomeJogador("");
      setCamisa("");
      aoMudar();
    } catch (erro) {
      aoErrar((erro as Error).message);
    } finally {
      setSalvando(false);
    }
  }

  return (
    <>
      <section className="cartao">
        <h2>Times</h2>
        <form className="linha-form" onSubmit={criarTime}>
          <input
            value={nomeTime}
            onChange={(e) => setNomeTime(e.target.value)}
            placeholder="Nome do time"
          />
          <button className="primario" disabled={salvando || !nomeTime.trim()}>
            Criar
          </button>
        </form>

        {times.length === 0 ? (
          <p className="vazio">Nenhum time cadastrado.</p>
        ) : (
          <ul className="lista">
            {times.map((t) => (
              <li key={t.id}>
                <span>{t.nome}</span>
                <span className="vazio">
                  {jogadores.filter((j) => j.time_id === t.id).length} jogador(es)
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="cartao">
        <h2>Jogadores</h2>
        <form onSubmit={criarJogador}>
          <div className="linha-form">
            <input
              value={nomeJogador}
              onChange={(e) => setNomeJogador(e.target.value)}
              placeholder="Nome do jogador"
            />
          </div>
          <div className="linha-form">
            <input
              value={camisa}
              onChange={(e) => setCamisa(e.target.value)}
              placeholder="Camisa"
              type="number"
              min="0"
              max="99"
              style={{ flex: "0 0 90px" }}
            />
            <select
              value={timeDoJogador}
              onChange={(e) => setTimeDoJogador(e.target.value)}
            >
              <option value="">Time…</option>
              {times.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.nome}
                </option>
              ))}
            </select>
            <button
              className="primario"
              disabled={salvando || !nomeJogador.trim() || !timeDoJogador}
            >
              Criar
            </button>
          </div>
        </form>

        {times.length === 0 && (
          <p className="vazio">Crie um time antes de cadastrar jogadores.</p>
        )}
      </section>
    </>
  );
}
