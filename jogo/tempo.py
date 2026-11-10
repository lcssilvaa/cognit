"""Política de tempo compartilhada pelo modo solo e pelo servidor de salas."""

from config import ESPERA_DICA, REDUCAO_POR_PERGUNTA, TEMPO_INICIAL, TEMPO_MINIMO


def limite_da_pergunta(indice):
    """Índice começa em zero; o piso impede perguntas sem tempo de leitura."""
    return max(TEMPO_MINIMO, TEMPO_INICIAL - indice * REDUCAO_POR_PERGUNTA)


def espera_da_dica(limite):
    """Mantém a dica acessível mesmo ao personalizar perguntas muito curtas."""
    return min(ESPERA_DICA, limite / 2)
