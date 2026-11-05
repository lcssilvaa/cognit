"""Verifica as regras que não podem falhar durante uma apresentação."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "jogo"))

from partida import Partida


class TestPartida(unittest.TestCase):
    def test_cinco_acertos_levam_a_vitoria(self):
        partida = Partida()
        self.assertEqual(len(partida.perguntas), 5)
        for nivel in range(5):
            self.assertEqual(partida.indice, nivel)
            self.assertTrue(partida.responder(partida.pergunta["correta"]))
            self.assertEqual(partida.progresso, (nivel + 1) * 20)
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
        self.assertEqual(partida.progresso, 20)
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


if __name__ == "__main__":
    unittest.main()
