"""Gera a trilha original do Cognit, um loop instrumental de 20 segundos.

Somente para recriar o arquivo: pip install -r requirements-audio.txt
Depois: python scripts/gerar_musica.py. O jogo não depende dessa ferramenta.
"""

from array import array
from math import exp, pi, sin
from pathlib import Path

TAXA = 24000
BATIDA = 60 / 96
DURACAO = 32 * BATIDA
DESTINO = Path(__file__).resolve().parents[1] / "jogo" / "assets" / "musica_fundo.ogg"


def frequencia(nota):
    return 440 * 2 ** ((nota - 69) / 12)


def adicionar_nota(amostras, nota, inicio, duracao, volume, pad=False):
    hz = frequencia(nota)
    primeiro = round(inicio * TAXA)
    quantidade = round(duracao * TAXA)
    for i in range(quantidade):
        t = i / TAXA
        ataque = min(1, t / (0.3 if pad else 0.012))
        final = min(1, (duracao - t) / (0.4 if pad else 0.09))
        envelope = ataque * final * (1 if pad else exp(-4 * t / duracao))
        onda = sin(2 * pi * hz * t) + .12 * sin(4 * pi * hz * t)
        indice = (primeiro + i) % len(amostras)
        amostras[indice] += volume * envelope * onda


def gerar():
    import soundfile

    amostras = array("f", [0]) * round(DURACAO * TAXA)
    acordes = [(48, 55, 59, 64), (45, 52, 55, 60), (41, 48, 52, 57), (43, 50, 55, 59)]
    melodias = [
        [72, None, 76, None, 79, 76, 74, 71],
        [72, None, 76, 79, 76, None, 72, None],
        [69, None, 72, None, 76, 72, 69, None],
        [71, None, 74, None, 79, 74, 71, None],
    ]
    for compasso, (acorde, melodia) in enumerate(zip(acordes, melodias)):
        inicio = compasso * 8 * BATIDA
        for nota in acorde:
            adicionar_nota(amostras, nota, inicio, 8 * BATIDA, .032, pad=True)
        for passo, nota in enumerate(melodia):
            if nota is not None:
                instante = inicio + passo * BATIDA
                adicionar_nota(amostras, nota, instante, BATIDA * .95, .08)
                adicionar_nota(amostras, nota, instante + .23, BATIDA * .95, .014)
    soundfile.write(DESTINO, amostras, TAXA, format="OGG", subtype="VORBIS")
    print(f"Trilha original criada: {DESTINO.name} ({DURACAO:.0f} s)")


if __name__ == "__main__":
    gerar()
