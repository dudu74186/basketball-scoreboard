use chrono::{DateTime, Utc};

// ---------------------------------------------------------------------------
// Times
// ---------------------------------------------------------------------------

#[derive(serde::Serialize)]
pub struct Time {
    pub id: i32,
    pub nome: String,
    pub criado_em: DateTime<Utc>,
}

#[derive(serde::Deserialize)]
pub struct NovoTime {
    pub nome: String,
}

// ---------------------------------------------------------------------------
// Jogadores
// ---------------------------------------------------------------------------

#[derive(serde::Serialize)]
pub struct Jogador {
    pub id: i32,
    pub nome: String,
    pub numero_camisa: Option<i16>,
    pub time_id: i32,
    pub criado_em: DateTime<Utc>,
}

#[derive(serde::Deserialize)]
pub struct NovoJogador {
    pub nome: String,
    pub numero_camisa: Option<i16>,
    pub time_id: i32,
}

// ---------------------------------------------------------------------------
// Partidas
// ---------------------------------------------------------------------------

#[derive(serde::Serialize)]
pub struct Partida {
    pub id: i32,
    pub modalidade: String,
    pub time_casa_id: i32,
    pub time_visitante_id: i32,
    pub data_hora: DateTime<Utc>,
    pub status: String,
    pub criado_em: DateTime<Utc>,
}

#[derive(serde::Deserialize)]
pub struct NovaPartida {
    pub modalidade: String,
    pub time_casa_id: i32,
    pub time_visitante_id: i32,
}

// ---------------------------------------------------------------------------
// Eventos
// ---------------------------------------------------------------------------

/// Tipo do evento como um enum, não como texto livre.
///
/// Vantagem: um `tipo` inválido é rejeitado já na desserialização do JSON
/// (vira 400 automaticamente), antes mesmo de chegar no banco. O `CHECK` da
/// migration continua lá como última linha de defesa — mas o ideal é a
/// requisição errada morrer o quanto antes.
#[derive(serde::Deserialize, serde::Serialize, Clone, Copy)]
pub enum TipoEvento {
    #[serde(rename = "cesta_2")]
    Cesta2,
    #[serde(rename = "cesta_3")]
    Cesta3,
    #[serde(rename = "lance_livre")]
    LanceLivre,
    #[serde(rename = "falta")]
    Falta,
}

impl TipoEvento {
    /// Quantos pontos esse tipo de evento vale.
    ///
    /// A pontuação é derivada aqui, no servidor — o cliente **não** envia
    /// `pontos`. Se enviasse, nada impediria alguém de registrar uma cesta de
    /// 2 valendo 50 pontos. Aqui a regra vive num lugar só.
    pub fn pontos(self) -> i16 {
        match self {
            TipoEvento::Cesta2 => 2,
            TipoEvento::Cesta3 => 3,
            TipoEvento::LanceLivre => 1,
            TipoEvento::Falta => 0,
        }
    }

    /// Como o valor é gravado na coluna `tipo` (bate com o CHECK da migration).
    pub fn como_texto(self) -> &'static str {
        match self {
            TipoEvento::Cesta2 => "cesta_2",
            TipoEvento::Cesta3 => "cesta_3",
            TipoEvento::LanceLivre => "lance_livre",
            TipoEvento::Falta => "falta",
        }
    }
}

#[derive(serde::Serialize)]
pub struct Evento {
    pub id: i32,
    pub partida_id: i32,
    pub jogador_id: i32,
    pub tipo: String,
    pub pontos: i16,
    pub tempo_video_ms: Option<i32>,
    pub criado_em: DateTime<Utc>,
}

#[derive(serde::Deserialize)]
pub struct NovoEvento {
    pub jogador_id: i32,
    pub tipo: TipoEvento,
    /// Posição no vídeo onde o evento aconteceu, em milissegundos.
    /// Opcional: um evento lançado à mão não tem vídeo por trás.
    pub tempo_video_ms: Option<i32>,
}

// ---------------------------------------------------------------------------
// Súmula
// ---------------------------------------------------------------------------

#[derive(serde::Serialize)]
pub struct LinhaSumula {
    pub jogador_id: i32,
    pub jogador_nome: String,
    pub time_id: i32,
    pub time_nome: String,
    pub pontos_totais: i64,
    pub faltas: i64,
}
