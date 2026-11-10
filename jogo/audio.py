"""Música de fundo independente das regras e das telas.

A trilha é carregada uma única vez. Falta de áudio não impede jogar.
No navegador, iniciar() é chamado depois de um clique, toque ou tecla.
"""

from pathlib import Path

import pygame

from config import MUSICA_ATIVA, VOLUME_MUSICA


class MusicaFundo:
    def __init__(self):
        self.habilitada = MUSICA_ATIVA
        self.carregada = False
        self.tocando = False
        self.pausada = False
        self.erro = None

    def iniciar(self):
        if not self.habilitada or self.tocando:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=24000, size=-16, channels=2, buffer=1024)
            if not self.carregada:
                caminho = Path(__file__).resolve().parent / "assets" / "musica_fundo.ogg"
                pygame.mixer.music.load(str(caminho))
                pygame.mixer.music.set_volume(VOLUME_MUSICA)
                self.carregada = True
            if self.pausada:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.play(loops=-1, fade_ms=800)
            self.tocando = True
            self.pausada = False
            self.erro = None
        except (pygame.error, OSError) as erro:
            self.erro = str(erro)

    def alternar(self):
        self.habilitada = not self.habilitada
        if self.habilitada:
            self.iniciar()
        elif self.carregada and pygame.mixer.get_init():
            pygame.mixer.music.pause()
            self.tocando = False
            self.pausada = True

    def encerrar(self):
        if self.carregada and pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        self.carregada = self.tocando = self.pausada = False
