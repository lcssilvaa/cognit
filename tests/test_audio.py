"""Valida o arquivo real e o controle de música sem depender de alto-falantes."""

import os
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "jogo"))

import pygame
from audio import MusicaFundo
from config import VOLUME_MUSICA


class TestAudio(unittest.TestCase):
    def setUp(self):
        pygame.mixer.quit()
        self.musica = MusicaFundo()

    def tearDown(self):
        self.musica.encerrar()
        pygame.mixer.quit()

    def test_trilha_real_carrega_e_toca_em_volume_baixo(self):
        self.musica.iniciar()
        self.assertTrue(pygame.mixer.music.get_busy())
        self.assertIsNone(self.musica.erro)
        self.assertAlmostEqual(pygame.mixer.music.get_volume(), VOLUME_MUSICA, delta=.01)
        arquivo = Path(__file__).resolve().parents[1] / "jogo/assets/musica_fundo.ogg"
        self.assertAlmostEqual(pygame.mixer.Sound(str(arquivo)).get_length(), 20, delta=.1)

    def test_desligar_e_religar_retomam_a_musica(self):
        self.musica.iniciar()
        self.musica.alternar()
        self.assertFalse(self.musica.habilitada)
        self.assertFalse(pygame.mixer.music.get_busy())
        self.musica.iniciar()  # Cliques nas outras ações respeitam a escolha.
        self.assertFalse(pygame.mixer.music.get_busy())
        self.musica.alternar()
        self.assertTrue(self.musica.habilitada)
        self.assertTrue(pygame.mixer.music.get_busy())

    def test_sem_dispositivo_de_audio_o_jogo_pode_continuar(self):
        with patch("pygame.mixer.init", side_effect=pygame.error("Sem dispositivo")):
            self.musica.iniciar()
        self.assertFalse(self.musica.carregada)
        self.assertFalse(self.musica.tocando)
        self.assertIsNotNone(self.musica.erro)

    def test_navegador_usa_player_nativo_sem_inicializar_mixer(self):
        janela = Mock()
        estado = {"carregada": True, "tocando": True, "pausada": False, "erro": None}
        janela.cognit_audio_estado.return_value = json.dumps(estado)
        with (patch("audio.sys.platform", "emscripten"),
              patch("audio.platform.window", janela, create=True), patch("pygame.mixer.init") as mixer):
            musica = MusicaFundo()
            musica.iniciar()
            self.assertTrue(musica.carregada)
            self.assertTrue(musica.tocando)
            musica.alternar()
            self.assertFalse(musica.habilitada)
            janela.cognit_audio_configurar.assert_called_with(False, VOLUME_MUSICA)
            musica.iniciar()
            janela.cognit_audio_iniciar.assert_called_once()
            musica.alternar()
            janela.cognit_audio_configurar.assert_called_with(True, VOLUME_MUSICA)
            musica.encerrar()
            janela.cognit_audio_encerrar.assert_called_once()
            mixer.assert_not_called()
