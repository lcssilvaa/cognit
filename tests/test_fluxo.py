"""Exercita telas e ações reais sem abrir uma janela na área de trabalho."""

import asyncio
import os
from pathlib import Path
import json
import sys
from threading import Thread
from time import monotonic
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "jogo"))

import pygame
from main import Jogo
from rede import ClienteSalas
from servidor import ServidorSalas
from temas import TEMAS
from config import ALTURA, CORES, LARGURA


class TestFluxo(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.servidor = ServidorSalas(("127.0.0.1", 0))
        self.thread = Thread(target=self.servidor.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.servidor.server_port}"
        self.jogo = Jogo()
        self.jogo.salas.endereco = self.url

    async def asyncTearDown(self):
        await self.jogo.salas.fechar()
        self.jogo.musica.encerrar()
        await asyncio.to_thread(self.servidor.shutdown)
        self.servidor.server_close()
        self.thread.join(timeout=2)
        pygame.quit()

    async def aguardar(self, condicao):
        prazo = monotonic() + 4
        while monotonic() < prazo:
            self.jogo.atualizar()
            self.jogo.desenhar()
            if condicao():
                return
            await asyncio.sleep(0.01)
        self.fail("O fluxo não chegou ao estado esperado: " + self.jogo.salas.erro)

    def clicar(self, acao, toque=False):
        """Aciona a área desenhada, passando pela conversão de coordenadas do jogo."""
        jogo = self.jogo
        jogo.desenhar()
        self.assertIn(acao, [a for _, a in jogo.ui.botoes])
        area = next(area for area, a in jogo.ui.botoes if a == acao)
        x = jogo.area_jogo.x + area.centerx * jogo.area_jogo.width / LARGURA
        y = jogo.area_jogo.y + area.centery * jogo.area_jogo.height / ALTURA
        if toque:
            largura, altura = jogo.janela.get_size()
            evento = pygame.event.Event(pygame.FINGERUP, x=x / largura, y=y / altura)
        else:
            evento = pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(x, y), button=1)
        jogo.tratar_evento(evento)

    async def test_solo_dica_pausa_e_timeout(self):
        jogo = self.jogo
        jogo.executar_acao("jogar")
        jogo.desenhar()
        self.assertNotIn("dica", [a for _, a in jogo.ui.botoes])
        jogo.partida.atualizar_tempo(8)
        jogo.desenhar()
        self.assertIn("dica", [a for _, a in jogo.ui.botoes])
        jogo.executar_acao("dica")
        self.assertTrue(jogo.partida.dica_visivel)
        jogo.executar_acao("confirmar_saida")
        restante = jogo.partida.tempo_restante
        with patch("main.monotonic", return_value=jogo.ultima_atualizacao + 60):
            jogo.atualizar()
            self.assertEqual(jogo.partida.tempo_restante, restante)
            jogo.executar_acao("pergunta")
        jogo.ultima_atualizacao = monotonic()
        jogo.partida.atualizar_tempo(jogo.partida.tempo_restante)
        jogo.atualizar()
        jogo.desenhar()
        self.assertEqual(jogo.tela_atual, "feedback")
        self.assertEqual(jogo.partida.vidas, 2)
        jogo.executar_acao("continuar")
        self.assertEqual(jogo.tela_atual, "pergunta")
        self.assertGreater(jogo.partida.tempo_restante, 44)

    async def test_web_preenche_tela_e_mantem_os_alvos_de_toque(self):
        jogo = self.jogo
        for tamanho in ((720, 1440), (824, 1700), (780, 1688), (1440, 720)):
            with self.subTest(tamanho=tamanho), patch("main.sys.platform", "emscripten"), \
                    patch("main.platform.window", SimpleNamespace(cognit_resolucao=tamanho,
                          cognit_campos_ocultar=lambda: None), create=True):
                jogo.desenhar()
                self.assertEqual(jogo.area_jogo, jogo.janela.get_rect())
                self.assertEqual(jogo.tela.get_size(), tamanho)
                for area, acao in jogo.ui.botoes:
                    pixel = jogo.ui.retangulo(area).center
                    self.assertEqual(jogo.ui.acao_clicada(jogo.posicao_logica(pixel)), acao)
                imagem = jogo.ui.imagem("marca.svg", 64, 64)
                self.assertEqual(imagem.get_width(), imagem.get_height())

    async def test_campos_web_sincronizam_texto_sem_duplicar_eventos_pygame(self):
        janela = Mock()
        janela.cognit_campos_ler.return_value = json.dumps({
            "valores": {"nome": "José 🧠", "codigo": "00a1234"}, "ativo": "nome"})
        salas = self.jogo.salas
        with patch("main.sys.platform", "emscripten"), patch("main.platform.window", janela, create=True):
            salas.sincronizar_campos_web()
            self.assertEqual(salas.campos, {"nome": "José 🧠", "codigo": "001234"})
            salas._editar_campo("nome")
            janela.cognit_campo_focar.assert_called_once_with("nome")
            self.assertTrue(salas.tratar_texto(pygame.event.Event(pygame.TEXTINPUT, text="José 🧠")))
            self.assertTrue(salas.tratar_texto(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE, mod=0)))
            self.assertEqual(salas.campos["nome"], "José 🧠")

    async def test_controle_de_musica_preserva_a_pergunta(self):
        jogo = self.jogo
        jogo.executar_acao("jogar")
        jogo.partida.atualizar_tempo(7)
        restante = jogo.partida.tempo_restante
        jogo.tratar_evento(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m, mod=0))
        self.assertFalse(jogo.musica.habilitada)
        self.assertEqual(jogo.tela_atual, "pergunta")
        self.assertEqual(jogo.partida.indice, 0)
        self.assertAlmostEqual(jogo.partida.tempo_restante, restante, delta=.2)
        jogo.executar_acao("alternar_musica")
        self.assertTrue(jogo.musica.habilitada)

    async def test_vitoria_solo_exibe_barra_completa(self):
        jogo = self.jogo
        jogo.executar_acao("jogar")
        for pergunta in jogo.partida.perguntas:
            jogo.executar_acao(f"resposta_{pergunta['correta']}")
            jogo.executar_acao("continuar")
        jogo.desenhar()
        self.assertEqual(jogo.tela_atual, "vitoria")
        self.assertEqual(jogo.partida.progresso, 100)
        # As duas extremidades internas da barra estão preenchidas no resultado.
        for x in (80, 310):
            self.assertEqual(jogo.tela.get_at(jogo.ui.ponto((x, 589))), pygame.Color(CORES["verde"]))

    async def test_formulario_unicode_e_disputa_completa(self):
        jogo = self.jogo
        jogo.executar_acao("amigos")
        jogo.desenhar()
        jogo.executar_acao("campo_nome")
        jogo.tratar_evento(pygame.event.Event(pygame.TEXTINPUT, text="João"))
        jogo.tratar_evento(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0))
        self.assertEqual(jogo.salas.campos["nome"], "João")
        await self.aguardar(lambda: jogo.salas.tema is not None and jogo.salas.tarefa is None)
        self.assertEqual([t["id"] for t in jogo.salas.temas], ["tecnologia", "ux_design"])
        self.assertNotIn("servidor", jogo.salas.campos)
        self.assertNotIn("campo_servidor", [a for _, a in jogo.ui.botoes])
        jogo.executar_acao("sala_escolher_icone")
        jogo.desenhar()
        jogo.executar_acao("sala_icone_vice_city")
        jogo.executar_acao("sala_usar_icone")
        jogo.executar_acao("sala_criar")
        await self.aguardar(lambda: jogo.tela_atual == "sala")
        self.assertEqual(jogo.salas.estado["voce"]["icone"], "vice_city")
        codigo = jogo.salas.estado["codigo"]
        cliente = ClienteSalas(self.url)
        amigo = await cliente.requisitar("entrar", {"codigo": codigo, "nome": "Maria"})
        await self.aguardar(lambda: len(jogo.salas.estado["jogadores"]) == 2)
        jogo.executar_acao("sala_iniciar")
        await self.aguardar(lambda: jogo.salas.estado["fase"] == "pergunta")
        total = jogo.salas.estado["total"]
        for indice in range(total):
            jogo.executar_acao("resposta_0")
            await self.aguardar(lambda: jogo.salas.estado["voce"]["respondeu"])
            self.assertNotIn("ganho", jogo.salas.estado["voce"])
            await cliente.requisitar("responder", {"codigo": codigo, "token": amigo["token"],
                                                  "indice": indice, "alternativa": 1})
            await self.aguardar(lambda: jogo.salas.estado["fase"] == "placar")
            self.assertIn(jogo.salas.estado["voce"]["resultado"], ("acertou", "errou"))
            self.assertIn("sala_ver_placar", [a for _, a in jogo.ui.botoes])
            jogo.executar_acao("sala_ver_placar")
            jogo.desenhar()
            jogo.executar_acao("sala_proxima")
            fase = "final" if indice == total - 1 else "pergunta"
            await self.aguardar(lambda: jogo.salas.estado["fase"] == fase)
        self.assertEqual(len(jogo.salas.estado["jogadores"]), 2)
        self.assertIn("sala_rever_podio", [a for _, a in jogo.ui.botoes])
        jogo.salas.fase_em -= 3
        jogo.desenhar()
        jogador_id = jogo.salas.estado["jogadores"][0]["id"]
        jogo.executar_acao("sala_podio_" + jogador_id)
        self.assertEqual(jogo.salas.detalhe_podio, jogador_id)
        jogo.executar_acao("sala_rever_podio")
        jogo.executar_acao("sala_confirmar_saida")
        await self.aguardar(lambda: jogo.tela_atual == "amigos")
        self.assertIsNone(jogo.salas.token)

    async def test_menu_atualiza_temas_a_partir_do_catalogo(self):
        jogo = self.jogo
        jogo.executar_acao("amigos")
        await self.aguardar(lambda: bool(jogo.salas.temas) and not jogo.salas.ocupado)
        self.assertIn("sala_escolher_tema", [a for _, a in jogo.ui.botoes])
        novo = {"nome": "Novo tema", "perguntas": TEMAS["tecnologia"]["perguntas"][:2]}
        with patch.dict(TEMAS, {"novo": novo}):
            jogo.executar_acao("inicio")
            jogo.executar_acao("amigos")
            await self.aguardar(lambda: len(jogo.salas.temas) == 3 and not jogo.salas.ocupado)
            self.clicar("sala_escolher_tema")
            self.clicar("sala_temas_proxima")
            self.clicar("sala_temas_anterior")
            self.clicar("sala_temas_proxima")
            self.clicar("sala_tema_novo")
            self.assertEqual(jogo.salas.tema, "novo")
            jogo.salas.campos["nome"] = "Teste"
            jogo.executar_acao("sala_criar")
            await self.aguardar(lambda: jogo.tela_atual == "sala")
            self.assertEqual(jogo.salas.estado["nome_tema"], "Novo tema")
            self.assertEqual(jogo.salas.estado["total"], 2)
            jogo.executar_acao("sala_confirmar_saida")
            await self.aguardar(lambda: jogo.tela_atual == "amigos")

    async def test_selecao_de_tema_por_clique_toque_e_teclado(self):
        jogo = self.jogo
        jogo.executar_acao("amigos")
        await self.aguardar(lambda: bool(jogo.salas.temas) and not jogo.salas.ocupado)
        jogo.salas.campos["nome"] = "João"
        jogo.salas.icone = "vice_city"
        self.clicar("sala_escolher_tema")
        jogo.desenhar()
        self.assertTrue(jogo.salas.escolhendo_tema)
        self.assertIn("sala_tema_tecnologia", [a for _, a in jogo.ui.botoes])
        self.assertIn("sala_tema_ux_design", [a for _, a in jogo.ui.botoes])
        self.assertNotIn("sala_criar", [a for _, a in jogo.ui.botoes])
        self.clicar("sala_tema_ux_design", toque=True)
        self.assertEqual(jogo.salas.tema, "ux_design")
        self.assertFalse(jogo.salas.escolhendo_tema)

        self.clicar("sala_escolher_tema")
        jogo.tratar_evento(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0))
        self.assertEqual(jogo.tela_atual, "amigos")
        self.assertFalse(jogo.salas.escolhendo_tema)
        self.assertEqual(jogo.salas.tema, "ux_design")
        self.clicar("sala_escolher_tema")
        jogo.desenhar()
        # O primeiro Tab foca Voltar; o segundo foca o cartão Tecnologia.
        for tecla in (pygame.K_TAB, pygame.K_TAB, pygame.K_RETURN):
            jogo.tratar_evento(pygame.event.Event(pygame.KEYDOWN, key=tecla, mod=0))
        self.assertEqual(jogo.salas.tema, "tecnologia")
        self.assertFalse(jogo.salas.escolhendo_tema)
        self.assertEqual(jogo.salas.campos["nome"], "João")
        self.assertEqual(jogo.salas.icone, "vice_city")
        self.clicar("sala_criar")
        await self.aguardar(lambda: jogo.tela_atual == "sala")
        self.assertEqual(jogo.salas.estado["nome_tema"], "Tecnologia")
        self.assertEqual(jogo.salas.estado["voce"]["icone"], "vice_city")

    async def test_ux_design_usa_o_mesmo_tema_nos_dois_modos(self):
        jogo = self.jogo
        perguntas = TEMAS["ux_design"]["perguntas"]
        self.assertEqual(len(perguntas), 10)
        jogo.executar_acao("temas")
        jogo.desenhar()
        temas_solo = [acao.removeprefix("tema_solo_") for _, acao in jogo.ui.botoes
                      if acao.startswith("tema_solo_")]
        jogo.executar_acao("tema_solo_ux_design")
        self.assertIs(jogo.partida.perguntas, perguntas)
        for pergunta in perguntas:
            jogo.executar_acao(f"resposta_{pergunta['correta']}")
            jogo.executar_acao("continuar")
        self.assertEqual(jogo.tela_atual, "vitoria")
        self.assertEqual(jogo.partida.progresso, 100)

        jogo.executar_acao("amigos")
        await self.aguardar(lambda: bool(jogo.salas.temas) and not jogo.salas.ocupado)
        self.assertEqual(temas_solo, [tema["id"] for tema in jogo.salas.temas])
        self.clicar("sala_escolher_tema")
        self.clicar("sala_tema_ux_design")
        self.assertEqual(jogo.salas.tema, "ux_design")
        jogo.salas.campos["nome"] = "Designer"
        jogo.executar_acao("sala_criar")
        await self.aguardar(lambda: jogo.tela_atual == "sala")
        codigo = jogo.salas.estado["codigo"]
        cliente = ClienteSalas(self.url)
        amigo = await cliente.requisitar("entrar", {"codigo": codigo, "nome": "Colega"})
        await self.aguardar(lambda: len(jogo.salas.estado["jogadores"]) == 2)
        jogo.executar_acao("sala_iniciar")
        await self.aguardar(lambda: jogo.salas.estado["fase"] == "pergunta")
        for indice, pergunta in enumerate(perguntas):
            self.assertEqual(jogo.salas.estado["pergunta"]["enunciado"], pergunta["enunciado"])
            self.assertEqual(jogo.salas.estado["pergunta"]["alternativas"], pergunta["alternativas"])
            jogo.executar_acao(f"resposta_{pergunta['correta']}")
            await self.aguardar(lambda: jogo.salas.estado["voce"]["respondeu"])
            await cliente.requisitar("responder", {"codigo": codigo, "token": amigo["token"],
                                                  "indice": indice, "alternativa": pergunta["correta"]})
            await self.aguardar(lambda: jogo.salas.estado["fase"] == "placar")
            jogo.executar_acao("sala_ver_placar")
            jogo.executar_acao("sala_proxima")
            fase = "final" if indice == len(perguntas) - 1 else "pergunta"
            await self.aguardar(lambda: jogo.salas.estado["fase"] == fase)
        self.assertEqual(jogo.salas.estado["nome_tema"], "UX e Design")
        self.assertTrue(all(j["acertos"] == 10 for j in jogo.salas.estado["jogadores"]))
