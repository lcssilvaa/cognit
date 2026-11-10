"""Simula relógio e jogadores para verificar justiça e sincronização das salas."""

import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "jogo"))

from config import ESPERA_DICA, EXPIRACAO_SALA, MAX_JOGADORES, TEMPO_DESCONEXAO
from salas import ErroSala, GerenciadorSalas
from temas import TEMAS
from avatares import AVATARES


class TestSalas(unittest.TestCase):
    def setUp(self):
        self.agora = 100.0
        self.salas = GerenciadorSalas(lambda: self.agora)
        self.host = self.salas.executar("criar", {"nome": "Ana", "tema": "tecnologia"})
        self.codigo = self.host["codigo"]
        self.amigo = self.salas.executar("entrar", {"codigo": self.codigo, "nome": "Bia"})

    def acao(self, acao, jogador=None, **dados):
        jogador = jogador or self.host
        return self.salas.executar(acao, {"codigo": self.codigo, "token": jogador["token"], **dados})

    def test_lobby_tema_codigo_e_tokens_privados(self):
        self.assertEqual(len(self.codigo), 6)
        self.assertTrue(self.codigo.isdigit())
        estado = self.acao("estado")
        self.assertEqual(len(estado["jogadores"]), 2)
        self.assertNotIn("token", estado)
        self.assertNotIn("pergunta", estado)
        self.assertNotIn(self.amigo["token"], str(estado))

    def test_so_host_inicia_e_precisa_de_dois_jogadores(self):
        with self.assertRaises(ErroSala):
            self.acao("iniciar", self.amigo)
        self.acao("sair", self.amigo)
        with self.assertRaises(ErroSala):
            self.acao("iniciar")

    def test_dica_aguarda_servidor_e_nao_vaza_gabarito(self):
        estado = self.acao("iniciar")
        self.assertNotIn("correta", estado)
        self.assertNotIn("explicacao", estado)
        self.assertNotIn("dica", estado["pergunta"])
        with self.assertRaises(ErroSala):
            self.acao("dica", indice=0)
        self.agora += ESPERA_DICA
        estado = self.acao("dica", indice=0)
        self.assertTrue(estado["dica"])
        self.assertNotIn("dica", self.acao("estado", self.amigo))
        self.assertTrue(estado["voce"]["usou_dica"])

    def test_todos_respondem_entao_placar_e_proxima_com_menos_tempo(self):
        inicio = self.acao("iniciar")
        resposta = TEMAS["tecnologia"]["perguntas"][0]["correta"]
        primeiro = self.acao("responder", indice=0, alternativa=resposta)
        self.assertEqual(primeiro["fase"], "pergunta")
        segundo = self.acao("responder", self.amigo, indice=0, alternativa=0)
        self.assertEqual(segundo["fase"], "placar")
        self.assertEqual(segundo["correta"], resposta)
        self.assertEqual(segundo["jogadores"][0]["pontos"], 1000)
        with self.assertRaises(ErroSala):
            self.acao("proxima", self.amigo)
        proxima = self.acao("proxima")
        self.assertEqual(proxima["indice"], 1)
        self.assertLess(proxima["limite"], inicio["limite"])
        self.assertFalse(proxima["voce"]["respondeu"])

    def test_resposta_duplicada_ou_atrasada_nao_da_pontos(self):
        self.acao("iniciar")
        correta = TEMAS["tecnologia"]["perguntas"][0]["correta"]
        self.acao("responder", indice=0, alternativa=correta)
        with self.assertRaises(ErroSala):
            self.acao("responder", indice=0, alternativa=correta)
        self.agora += 45
        self.acao("estado")  # O host continua consultando durante a espera.
        with self.assertRaises(ErroSala):
            self.acao("responder", self.amigo, indice=0, alternativa=correta)
        estado = self.acao("estado", self.amigo)
        self.assertEqual(estado["fase"], "placar")
        self.assertEqual(estado["voce"]["pontos"], 0)
        self.assertEqual(estado["jogadores"][0]["pontos"], 1000)
        self.acao("proxima")
        with self.assertRaises(ErroSala):
            self.acao("responder", indice=0, alternativa=correta)

    def test_indice_da_pergunta_precisa_ser_inteiro(self):
        self.acao("iniciar")
        self.agora += ESPERA_DICA
        for indice in (False, 0.0, "0", None):
            for acao in ("dica", "responder"):
                with self.subTest(indice=indice, acao=acao):
                    with self.assertRaises(ErroSala):
                        self.acao(acao, indice=indice, alternativa=1)
        estado = self.acao("estado")
        self.assertFalse(estado["voce"]["respondeu"])
        self.assertFalse(estado["voce"]["usou_dica"])
        self.assertEqual(estado["voce"]["pontos"], 0)

    def test_pontos_por_velocidade_e_desconto_da_dica(self):
        self.acao("iniciar")
        self.agora += ESPERA_DICA
        self.acao("dica", indice=0)
        self.acao("dica", indice=0)  # Reabrir não acumula penalidades.
        correta = TEMAS["tecnologia"]["perguntas"][0]["correta"]
        host = self.acao("responder", indice=0, alternativa=correta)
        amigo = self.acao("responder", self.amigo, indice=0, alternativa=correta)
        host = self.acao("estado")
        self.assertEqual(amigo["voce"]["pontos"] - host["voce"]["pontos"], 200)
        self.assertLess(amigo["voce"]["pontos"], 1000)

    def test_timeout_libera_placar_e_partida_completa_tem_resultado(self):
        estado = self.acao("iniciar")
        for i in range(estado["total"]):
            self.agora += estado["limite"]
            estado = self.acao("estado")
            self.assertEqual(estado["fase"], "placar")
            estado = self.acao("proxima")
        self.assertEqual(estado["fase"], "final")
        self.assertEqual(estado["voce"]["pontos"], 0)

    def test_saida_transfere_anfitriao_e_remove_sala_vazia(self):
        self.acao("sair")
        self.assertTrue(self.acao("estado", self.amigo)["anfitriao"])
        self.acao("sair", self.amigo)
        self.assertNotIn(self.codigo, self.salas.salas)

    def test_sala_expira_sem_atividade(self):
        self.agora += EXPIRACAO_SALA
        with self.assertRaises(ErroSala):
            self.acao("estado")

    def test_anfitriao_desconectado_e_substituido_sem_apagar_pontos(self):
        self.agora += TEMPO_DESCONEXAO
        estado = self.acao("estado", self.amigo)
        self.assertTrue(estado["anfitriao"])
        self.assertEqual(len(estado["jogadores"]), 2)
        host = next(j for j in estado["jogadores"] if j["nome"] == "Ana")
        self.assertFalse(host["online"])
        self.assertFalse(self.acao("estado")["anfitriao"])

    def test_valida_apelidos_tema_token_e_lotacao(self):
        for dados in ({"nome": ""}, {"nome": "X", "tema": []}):
            with self.assertRaises(ErroSala):
                self.salas.executar("criar", dados)
        with self.assertRaises(ErroSala):
            self.salas.executar("entrar", {"codigo": self.codigo, "nome": "ana"})
        with self.assertRaises(ErroSala):
            self.salas.executar("estado", {"codigo": self.codigo, "token": "invalido"})
        for i in range(MAX_JOGADORES - 2):
            self.salas.executar("entrar", {"codigo": self.codigo, "nome": str(i)})
        with self.assertRaises(ErroSala):
            self.salas.executar("entrar", {"codigo": self.codigo, "nome": "Extra"})

    def test_nao_aceita_entrada_durante_partida(self):
        self.acao("iniciar")
        with self.assertRaises(ErroSala):
            self.salas.executar("entrar", {"codigo": self.codigo, "nome": "Atrasado"})

    def test_respostas_concorrentes_nao_duplicam_pontuacao(self):
        self.acao("iniciar")
        correta = TEMAS["tecnologia"]["perguntas"][0]["correta"]
        def responder(_):
            try:
                return self.acao("responder", indice=0, alternativa=correta)
            except ErroSala:
                return None
        with ThreadPoolExecutor(max_workers=8) as executor:
            resultados = list(executor.map(responder, range(8)))
        self.assertEqual(sum(r is not None for r in resultados), 1)
        self.assertEqual(self.acao("estado")["voce"]["pontos"], 0)
        self.acao("responder", self.amigo, indice=0, alternativa=0)
        self.assertEqual(self.acao("estado")["voce"]["pontos"], 1000)

    def test_ganho_resultado_e_acertos_so_sao_revelados_ao_encerrar(self):
        self.acao("iniciar")
        estado = self.acao("responder", indice=0, alternativa=1)
        self.assertEqual(estado["fase"], "pergunta")
        self.assertNotIn("ganho", estado["voce"])
        self.assertNotIn("resultado", estado["voce"])
        self.assertEqual(estado["voce"]["pontos"], 0)
        self.assertTrue(all(j["pontos"] == j["acertos"] == 0 for j in estado["jogadores"]))
        self.assertEqual([j["nome"] for j in estado["jogadores"]], ["Ana", "Bia"])
        self.acao("responder", self.amigo, indice=0, alternativa=0)
        fechado = self.acao("estado")
        self.assertEqual(fechado["voce"]["ganho"], 1000)
        self.assertEqual(fechado["voce"]["resultado"], "acertou")
        self.assertEqual(self.acao("estado", self.amigo)["voce"]["resultado"], "errou")
        self.acao("proxima")
        self.acao("responder", indice=1, alternativa=2)
        self.assertEqual(self.acao("estado")["voce"]["pontos"], 1000)
        # No timeout, soma a segunda rodada apenas uma vez.
        self.agora += 42
        estado = self.acao("estado")
        self.assertEqual(estado["voce"]["pontos"], 2000)
        self.assertEqual(self.acao("estado")["voce"]["pontos"], 2000)
        self.assertEqual(self.acao("estado", self.amigo)["voce"]["resultado"], "sem_resposta")

    def test_posicao_pessoal_fora_do_top_cinco(self):
        outros = [self.amigo]
        for i in range(4):
            outros.append(self.salas.executar("entrar", {"codigo": self.codigo, "nome": f"Amigo {i}"}))
        self.acao("iniciar")
        for i, amigo in enumerate(outros):
            self.agora += 1
            self.acao("responder", amigo, indice=0, alternativa=1)
        self.acao("responder", indice=0, alternativa=0)
        estado = self.acao("estado")
        self.assertEqual(estado["voce"]["posicao"], 6)
        self.assertNotIn(estado["voce"]["id"], [j["id"] for j in estado["jogadores"][:5]])
        self.assertEqual([j["posicao"] for j in estado["jogadores"]], list(range(1, 7)))

    def test_empate_mantem_posicao_compartilhada(self):
        self.acao("iniciar")
        self.acao("responder", indice=0, alternativa=1)
        self.acao("responder", self.amigo, indice=0, alternativa=1)
        self.assertEqual([j["posicao"] for j in self.acao("estado")["jogadores"]], [1, 1])

    def test_catalogo_contem_apenas_cadastros_com_perguntas(self):
        self.assertEqual([t["id"] for t in self.salas.executar("catalogo", {})["temas"]], ["tecnologia", "ux_design"])
        with patch.dict(TEMAS, {"novo": {"nome": "Novo tema", "perguntas": TEMAS["tecnologia"]["perguntas"]},
                               "vazio": {"nome": "Em criação", "perguntas": []}}):
            catalogo = self.salas.executar("catalogo", {})["temas"]
            self.assertEqual([t["id"] for t in catalogo], ["tecnologia", "ux_design", "novo"])
            sala = self.salas.executar("criar", {"nome": "Teste", "tema": "novo"})
            self.assertEqual(sala["nome_tema"], "Novo tema")
            with self.assertRaises(ErroSala):
                self.salas.executar("criar", {"nome": "Teste", "tema": "vazio"})

    def test_icones_validos_aparecem_no_perfil_e_no_placar(self):
        for icone in AVATARES:
            sala = self.salas.executar("criar", {"nome": "Teste", "icone": icone})
            self.assertEqual(sala["voce"]["icone"], icone)
            self.assertEqual(sala["jogadores"][0]["icone"], icone)
        with self.assertRaises(ErroSala):
            self.salas.executar("entrar", {"codigo": self.codigo, "nome": "Invasor", "icone": "../arquivo"})

    def test_jogador_pode_marcar_pronto_no_lobby(self):
        estado = self.acao("pronto", self.amigo)
        self.assertTrue(estado["voce"]["pronto"])
        self.assertFalse(self.acao("pronto", self.amigo)["voce"]["pronto"])
        self.acao("iniciar")
        with self.assertRaises(ErroSala):
            self.acao("pronto", self.amigo)

    def test_temas_disponiveis_sao_jogaveis(self):
        for tema, cadastro in TEMAS.items():
            criada = self.salas.executar("criar", {"nome": "Teste", "tema": tema})
            self.assertEqual(criada["total"], len(cadastro["perguntas"]))
            self.assertTrue(all(p.get("dica") for p in cadastro["perguntas"]))
