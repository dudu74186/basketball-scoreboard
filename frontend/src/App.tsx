import { useCallback, useEffect, useState } from "react";
import type { Jogador, LinhaSumula, Partida, Time } from "./api";
import { api } from "./api";
import { PainelCadastro } from "./componentes/PainelCadastro";
import { PainelPartidas } from "./componentes/PainelPartidas";
import { PainelPlacar } from "./componentes/PainelPlacar";

export default function App() {
  const [times, setTimes] = useState<Time[]>([]);
  const [jogadores, setJogadores] = useState<Jogador[]>([]);
  const [partidas, setPartidas] = useState<Partida[]>([]);
  const [partidaAtiva, setPartidaAtiva] = useState<number | null>(null);
  const [sumula, setSumula] = useState<LinhaSumula[]>([]);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  const carregarCadastros = useCallback(async () => {
    try {
      const [t, j, p] = await Promise.all([
        api.listarTimes(),
        api.listarJogadores(),
        api.listarPartidas(),
      ]);
      setTimes(t);
      setJogadores(j);
      setPartidas(p);
      setApiOnline(true);
    } catch (e) {
      setApiOnline(false);
      setErro(
        `Não foi possível falar com a API: ${(e as Error).message}. ` +
          `A stack está no ar? (docker compose up -d)`,
      );
    }
  }, []);

  const carregarSumula = useCallback(async (partidaId: number) => {
    try {
      setSumula(await api.sumula(partidaId));
    } catch (e) {
      setErro((e as Error).message);
    }
  }, []);

  useEffect(() => {
    carregarCadastros();
  }, [carregarCadastros]);

  useEffect(() => {
    if (partidaAtiva !== null) carregarSumula(partidaAtiva);
  }, [partidaAtiva, carregarSumula]);

  // A súmula é recarregada periodicamente para refletir eventos que chegarem
  // por fora desta tela — é exatamente o caso do serviço de IA, que grava
  // via gRPC. Um WebSocket seria mais elegante; para um painel de operação,
  // recarregar a cada 3s resolve sem complexidade extra.
  useEffect(() => {
    if (partidaAtiva === null) return;
    const timer = setInterval(() => carregarSumula(partidaAtiva), 3000);
    return () => clearInterval(timer);
  }, [partidaAtiva, carregarSumula]);

  const partida = partidas.find((p) => p.id === partidaAtiva) ?? null;

  return (
    <div className="app">
      <header className="cabecalho">
        <h1>🏀 Placar Automático — painel de operação</h1>
        <span className="pilula">
          <span
            className={`ponto ${apiOnline === null ? "" : apiOnline ? "ok" : "ruim"}`}
          />
          {apiOnline === null ? "verificando…" : apiOnline ? "API online" : "API offline"}
        </span>
      </header>

      {erro && (
        <div className="alerta">
          <span>{erro}</span>
          <button onClick={() => setErro(null)} aria-label="Fechar aviso">
            ×
          </button>
        </div>
      )}

      <div className="colunas">
        <div>
          <PainelCadastro
            times={times}
            jogadores={jogadores}
            aoMudar={carregarCadastros}
            aoErrar={setErro}
          />
          <PainelPartidas
            times={times}
            partidas={partidas}
            partidaAtiva={partidaAtiva}
            aoSelecionar={setPartidaAtiva}
            aoMudar={carregarCadastros}
            aoErrar={setErro}
          />
        </div>

        <div>
          {partida ? (
            <PainelPlacar
              partida={partida}
              times={times}
              jogadores={jogadores}
              sumula={sumula}
              aoRegistrar={() => carregarSumula(partida.id)}
              aoErrar={setErro}
            />
          ) : (
            <section className="cartao">
              <h2>Partida</h2>
              <p className="vazio">
                Crie ou abra uma partida ao lado para registrar eventos e acompanhar a
                súmula.
              </p>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
