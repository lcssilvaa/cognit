"""Música de fundo independente das regras e das telas.

A trilha é carregada uma única vez. Falta de áudio não impede jogar.
No navegador, iniciar() é chamado depois de um clique, toque ou tecla.
"""

import json
from pathlib import Path
import platform
import sys

import pygame

from config import MUSICA_ATIVA, VOLUME_MUSICA


class MusicaFundo:
    def __init__(self):
        self.habilitada = MUSICA_ATIVA
        self.web = sys.platform == "emscripten"
        self._carregada = self._tocando = self._pausada = False
        self._erro = None
        if self.web:
            platform.window.cognit_audio_configurar(self.habilitada, VOLUME_MUSICA)

    def _estado(self, campo, desktop):
        if self.web:
            return json.loads(str(platform.window.cognit_audio_estado()))[campo]
        return desktop

    @property
    def carregada(self):
        return self._estado("carregada", self._carregada)

    @property
    def tocando(self):
        return self._estado("tocando", self._tocando)

    @property
    def pausada(self):
        return self._estado("pausada", self._pausada)

    @property
    def erro(self):
        return self._estado("erro", self._erro)

    def iniciar(self):
        if not self.habilitada:
            return
        if self.web:
            # A decodificação e a reprodução nativas não disputam o loop do jogo.
            platform.window.cognit_audio_iniciar()
            return
        if self.tocando:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=24000, size=-16, channels=2, buffer=1024)
            if not self.carregada:
                caminho = Path(__file__).resolve().parent / "assets" / "musica_fundo.ogg"
                pygame.mixer.music.load(str(caminho))
                pygame.mixer.music.set_volume(VOLUME_MUSICA)
                self._carregada = True
            if self.pausada:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.play(loops=-1, fade_ms=800)
            self._tocando = True
            self._pausada = False
            self._erro = None
        except (pygame.error, OSError) as erro:
            self._erro = str(erro)

    def alternar(self):
        self.habilitada = not self.habilitada
        if self.web:
            platform.window.cognit_audio_configurar(self.habilitada, VOLUME_MUSICA)
            return
        if self.habilitada:
            self.iniciar()
        elif self.carregada and pygame.mixer.get_init():
            pygame.mixer.music.pause()
            self._tocando = False
            self._pausada = True

    def encerrar(self):
        if self.web:
            platform.window.cognit_audio_encerrar()
            return
        if self.carregada and pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        self._carregada = self._tocando = self._pausada = False
