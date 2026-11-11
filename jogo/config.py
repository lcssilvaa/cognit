"""Personalize aqui o nome, as vidas e as cores do jogo."""

import os

TITULO = "Cognit"
LARGURA = 390
ALTURA = 844
FPS = 60
VIDAS_INICIAIS = 3

# A música é original, instrumental e toca em loop. Volume entre 0.0 e 1.0.
MUSICA_ATIVA = True
VOLUME_MUSICA = 0.22

# Tempos em segundos. A redução acontece ao avançar de pergunta.
TEMPO_INICIAL = 45
REDUCAO_POR_PERGUNTA = 3
TEMPO_MINIMO = 12
ESPERA_DICA = 8

# Salas no desktop: configure a API abaixo. O anfitrião também joga.
# Na versão web, a API vem de web/configuracao.json ou da variável de build.
SERVIDOR_PADRAO = os.environ.get("COGNIT_SERVIDOR", "http://localhost:8765")
INTERVALO_SINCRONIZACAO = 0.5
MAX_JOGADORES = 12
EXPIRACAO_SALA = 2 * 60 * 60
TEMPO_DESCONEXAO = 30
DURACAO_FEEDBACK_RODADA = 2.5

# As medidas seguem as telas de 390 x 844 da pasta prototipo.
CORES = {
    "fundo_inicio": "#F4F8FF",
    "fundo_fim": "#E4EEFB",
    "azul": "#1E5FA8",
    "azul_escuro": "#10294D",
    "azul_claro": "#EAF2FB",
    "texto": "#1F2937",
    "secundario": "#6B7280",
    "borda": "#D6E2F2",
    "branco": "#FFFFFF",
    "verde": "#209E70",
    "verde_claro": "#E3F6EC",
    "vermelho": "#E5484D",
    "vermelho_claro": "#FDEDEE",
    "roxo": "#7544CA",
    "roxo_claro": "#EDE9FE",
    "amarelo": "#FFB224",
    "amarelo_claro": "#FFF4DC",
    "desativado": "#9CA3AF",
}
