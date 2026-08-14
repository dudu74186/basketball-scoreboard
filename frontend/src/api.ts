// Cliente da API. Todos os tipos aqui espelham as structs do backend
// (backend/src/modelos.rs) — se mudar lá, mude aqui.

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:3000";

export type Time = {
  id: number;
  nome: string;
  criado_em: string;
};

export type Jogador = {
  id: number;
  nome: string;
  numero_camisa: number | null;
  time_id: number;
  criado_em: string;
};

export type Partida = {
  id: number;
  modalidade: string;
  time_casa_id: number;
  time_visitante_id: number;
  data_hora: string;
  status: string;
  criado_em: string;
};

export type Evento = {
  id: number;
  partida_id: number;
  jogador_id: number;
  tipo: TipoEvento;
  pontos: number;
  tempo_video_ms: number | null;
  criado_em: string;
};

export type LinhaSumula = {
  jogador_id: number;
  jogador_nome: string;
  time_id: number;
  time_nome: string;
  pontos_totais: number;
  faltas: number;
};

export type TipoEvento = "cesta_2" | "cesta_3" | "lance_livre" | "falta";

/** Erro vindo da API, já com a mensagem que o backend mandou em {"erro": ...}. */
export class ApiError extends Error {
  // Declarado como campo em vez de propriedade de construtor: o template do
  // Vite liga `erasableSyntaxOnly`, que só aceita sintaxe TypeScript
  // removível sem transformação de código.
  status: number;

  constructor(status: number, mensagem: string) {
    super(mensagem);
    this.status = status;
  }
}

async function requisitar<T>(rota: string, init?: RequestInit): Promise<T> {
  const resposta = await fetch(`${BASE}${rota}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });

  if (!resposta.ok) {
    // O backend padroniza erros como {"erro": "..."}, mas se algo passar por
    // fora disso (um proxy, por exemplo) não vale quebrar o app tentando
    // interpretar JSON.
    const corpo = await resposta.json().catch(() => null);
    throw new ApiError(resposta.status, corpo?.erro ?? `erro ${resposta.status}`);
  }

  return resposta.json();
}

export const api = {
  health: () => requisitar<{ status: string; banco: string }>("/health"),

  listarTimes: () => requisitar<Time[]>("/times"),
  criarTime: (nome: string) =>
    requisitar<Time>("/times", { method: "POST", body: JSON.stringify({ nome }) }),

  listarJogadores: (timeId?: number) =>
    requisitar<Jogador[]>(`/jogadores${timeId ? `?time_id=${timeId}` : ""}`),
  criarJogador: (dados: { nome: string; numero_camisa: number | null; time_id: number }) =>
    requisitar<Jogador>("/jogadores", { method: "POST", body: JSON.stringify(dados) }),

  listarPartidas: () => requisitar<Partida[]>("/partidas"),
  criarPartida: (dados: {
    modalidade: string;
    time_casa_id: number;
    time_visitante_id: number;
  }) => requisitar<Partida>("/partidas", { method: "POST", body: JSON.stringify(dados) }),

  listarEventos: (partidaId: number) =>
    requisitar<Evento[]>(`/partidas/${partidaId}/eventos`),
  // Note que não se envia `pontos`: quem decide é o servidor.
  registrarEvento: (partidaId: number, jogadorId: number, tipo: TipoEvento) =>
    requisitar<Evento>(`/partidas/${partidaId}/eventos`, {
      method: "POST",
      body: JSON.stringify({ jogador_id: jogadorId, tipo }),
    }),

  sumula: (partidaId: number) => requisitar<LinhaSumula[]>(`/partidas/${partidaId}/sumula`),
};
