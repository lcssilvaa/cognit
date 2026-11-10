"""Verifica as regras que não podem falhar durante uma apresentação."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "jogo"))

from partida import Partida
from config import ESPERA_DICA, TEMPO_MINIMO


class TestPartida(unittest.TestCase):
    def test_todos_os_acertos_levam_a_vitoria(self):
        partida = Partida()
        total = len(partida.perguntas)
        for nivel in range(total):
            self.assertEqual(partida.indice, nivel)
            self.assertTrue(partida.responder(partida.pergunta["correta"]))
            self.assertEqual(partida.progresso, round((nivel + 1) / total * 100))
            self.assertEqual(partida.venceu, nivel == total - 1)
            partida.continuar()
        self.assertTrue(partida.venceu)
        self.assertEqual(partida.vidas, 3)
        self.assertIsNone(partida.responder(0))

    def test_erro_perde_vida_e_permite_repetir_a_pergunta(self):
        partida = Partida()
        errada = (partida.pergunta["correta"] + 1) % len(partida.pergunta["alternativas"])
        self.assertFalse(partida.responder(errada))
        self.assertEqual(partida.vidas, 2)
        self.assertEqual(partida.progresso, 0)
        # Cliques extras antes de Continuar não descontam vidas.
        self.assertIsNone(partida.responder(errada))
        partida.continuar()
        self.assertEqual(partida.indice, 0)
        # A alternativa errada fica desativada nesta pergunta.
        self.assertIsNone(partida.responder(errada))
        self.assertEqual(partida.vidas, 2)
        self.assertTrue(partida.responder(partida.pergunta["correta"]))
        partida.continuar()
        self.assertEqual(partida.indice, 1)
        self.assertEqual(partida.alternativas_erradas, set())

    def test_tres_erros_encerram_a_partida(self):
        partida = Partida()
        for alternativa in [0, 2]:
            self.assertFalse(partida.responder(alternativa))
            partida.continuar()
        partida.responder(partida.pergunta["correta"])
        partida.continuar()
        partida.responder(0)  # Pergunta 2: a resposta correta é C.
        partida.continuar()
        self.assertTrue(partida.perdeu)
        self.assertFalse(partida.venceu)
        self.assertEqual(partida.vidas, 0)
        self.assertEqual(partida.progresso, round(100 / len(partida.perguntas)))
        self.assertIsNone(partida.responder(partida.pergunta["correta"]))

    def test_uma_nova_partida_reinicia_tudo(self):
        anterior = Partida()
        anterior.responder(0)
        nova = Partida()
        self.assertEqual(nova.vidas, 3)
        self.assertEqual(nova.acertos, 0)
        self.assertEqual(nova.erros, 0)
        self.assertEqual(nova.indice, 0)
        self.assertEqual(nova.alternativas_erradas, set())

    def test_resposta_fora_das_opcoes_e_ignorada(self):
        partida = Partida()
        self.assertIsNone(partida.responder(len(partida.pergunta["alternativas"])))
        self.assertIsNone(partida.responder(-1))
        self.assertEqual(partida.vidas, 3)
        self.assertIsNone(partida.ultimo_acerto)

    def test_personalizacao_de_perguntas_e_vidas(self):
        perguntas = [{"alternativas": ["A", "B", "C", "D"], "correta": 3}]
        partida = Partida(perguntas, vidas=1)
        self.assertTrue(partida.responder(3))
        partida.continuar()
        self.assertTrue(partida.venceu)
        self.assertEqual(partida.progresso, 100)

    def test_tempo_diminui_ao_avancar_e_respeita_piso(self):
        partida = Partida()
        anterior = partida.tempo_limite
        for pergunta in partida.perguntas[:-1]:
            partida.atualizar_tempo(2)
            partida.responder(pergunta["correta"])
            partida.continuar()
            self.assertLess(partida.tempo_limite, anterior)
            self.assertEqual(partida.tempo_restante, partida.tempo_limite)
            anterior = partida.tempo_limite
        partida.indice = 100
        self.assertEqual(partida.tempo_limite, TEMPO_MINIMO)

    def test_dica_so_abre_apos_espera_e_reinicia_no_proximo_nivel(self):
        partida = Partida()
        self.assertFalse(partida.revelar_dica())
        partida.atualizar_tempo(ESPERA_DICA - 0.01)
        self.assertFalse(partida.revelar_dica())
        partida.atualizar_tempo(0.01)
        self.assertTrue(partida.revelar_dica())
        partida.responder(partida.pergunta["correta"])
        partida.continuar()
        self.assertFalse(partida.dica_visivel)
        self.assertFalse(partida.revelar_dica())

    def test_timeout_perde_uma_vida_bloqueia_resposta_e_reinicia_tentativa(self):
        partida = Partida()
        partida.atualizar_tempo(partida.tempo_limite + 10)
        self.assertTrue(partida.tempo_esgotado)
        self.assertEqual(partida.vidas, 2)
        self.assertIsNone(partida.responder(partida.pergunta["correta"]))
        partida.atualizar_tempo(100)
        self.assertEqual(partida.vidas, 2)
        partida.continuar()
        self.assertEqual(partida.indice, 0)
        self.assertEqual(partida.tempo_restante, partida.tempo_limite)
        self.assertFalse(partida.tempo_esgotado)
        self.assertTrue(partida.responder(partida.pergunta["correta"]))

    def test_erro_preserva_prazo_e_feedback_nao_consume_tempo(self):
        partida = Partida()
        partida.atualizar_tempo(10)
        restante = partida.tempo_restante
        partida.responder(0)
        partida.atualizar_tempo(200)
        self.assertEqual(partida.tempo_restante, restante)
        partida.continuar()
        self.assertEqual(partida.tempo_restante, restante)

    def test_timeouts_podem_encerrar_a_partida(self):
        partida = Partida()
        for _ in range(3):
            partida.atualizar_tempo(partida.tempo_limite)
            partida.continuar()
        self.assertTrue(partida.perdeu)
        partida.atualizar_tempo(100)
        self.assertEqual(partida.vidas, 0)


if __name__ == "__main__":
    unittest.main()
