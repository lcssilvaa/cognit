"""Cognit: navegação entre telas e loop principal em Pygame.

Execute a partir da raiz: python jogo/main.py
Desenhos solo: visuais_solo.py | Salas: telas_sala.py | Regras solo: partida.py
"""

import asyncio
import platform
import sys
from time import monotonic

import pygame

from config import ALTURA, CORES, FPS, LARGURA, TITULO
from interface import Interface
from audio import MusicaFundo
from partida import Partida
from telas_sala import TelasSala
from temas import TEMAS, catalogo_temas
from visuais_solo import VisuaisSolo
from visuais_temas import TEMAS_POR_PAGINA


class Jogo:
    def __init__(self):
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_caption(f"{TITULO}")
        flags = 0 if sys.platform == "emscripten" else pygame.RESIZABLE
        self.janela = pygame.display.set_mode(self.tamanho_inicial(), flags)
        self.area_jogo = pygame.Rect(0, 0, LARGURA, ALTURA)
        self.calcular_area_jogo()
        self.tela = pygame.Surface(self.area_jogo.size)
        self.ui = Interface(self.tela)
        pygame.display.set_icon(self.ui.imagem("marca.png", 64, 64))
        self.partida = Partida()
        self.tema_solo = "tecnologia"
        self.pagina_temas = 0
        self.tela_atual = "inicio"
        self.rodando = True
        self.salas = TelasSala(self)
        self.visuais = VisuaisSolo(self)
        self.ultima_atualizacao = monotonic()
        self.musica = MusicaFundo()
        if sys.platform != "emscripten":
            self.musica.iniciar()

    def tamanho_inicial(self):
        """Mantém a proporção do protótipo e cabe em telas de notebook."""
        if sys.platform == "emscripten":
            return self.tamanho_web()
        altura_monitor = pygame.display.Info().current_h
        altura = min(ALTURA, max(480, altura_monitor - 110))
        return (round(LARGURA * altura / ALTURA), altura)

    def tamanho_web(self):
        medidas = platform.window.cognit_resolucao
        return (int(medidas[0]), int(medidas[1]))

    def atualizar_resolucao(self):
        """Acompanha o tamanho da janela e a densidade de pixels do celular."""
        if sys.platform == "emscripten":
            tamanho = self.tamanho_web()
            if self.janela.get_size() != tamanho:
                self.janela = pygame.display.set_mode(tamanho)
        self.calcular_area_jogo()
        if self.tela.get_size() != self.area_jogo.size:
            self.tela = pygame.Surface(self.area_jogo.size)
            self.ui.redimensionar(self.tela)

    def calcular_area_jogo(self):
        largura, altura = self.janela.get_size()
        if sys.platform == "emscripten":
            self.area_jogo = self.janela.get_rect()
            return
        escala = min(largura / LARGURA, altura / ALTURA)
        tamanho = (max(1, round(LARGURA * escala)), max(1, round(ALTURA * escala)))
        self.area_jogo = pygame.Rect((0, 0), tamanho)
        self.area_jogo.center = (largura // 2, altura // 2)

    def posicao_logica(self, posicao):
        """Converte o clique da janela redimensionada para as medidas do desenho."""
        if not self.area_jogo.collidepoint(posicao):
            return (-1, -1)
        x = (posicao[0] - self.area_jogo.x) * LARGURA / self.area_jogo.width
        y = (posicao[1] - self.area_jogo.y) * ALTURA / self.area_jogo.height
        return (x, y)

    def navegar(self, tela):
        # Contabiliza só o tempo passado na pergunta; navegar não reinicia o prazo.
        self.atualizar_tempo()
        self.tela_atual = tela
        self.salas.campo_ativo = None
        pygame.key.stop_text_input()
        self.ui.foco = 0
        self.ui.foco_ativo = False
        # Descarta botões da tela anterior antes do próximo evento.
        self.ui.botoes = []

    def executar_acao(self, acao):
        if acao is None:
            return
        self.atualizar_tempo()
        if acao == "alternar_musica":
            self.musica.alternar()
            return
        if acao == "amigos" or acao.startswith(("sala_", "campo_")) or self.tela_atual == "sala":
            self.salas.executar_acao(acao)
            return
        if acao in ("inicio", "temas", "ajuda", "confirmar_saida", "pergunta"):
            self.navegar(acao)
        elif acao in ("temas_anterior", "temas_proxima"):
            direcao = -1 if acao == "temas_anterior" else 1
            self.pagina_temas = max(0, min((len(catalogo_temas()) - 1) // TEMAS_POR_PAGINA, self.pagina_temas + direcao))
        elif acao == "jogar" or acao.startswith("tema_solo_"):
            if acao.startswith("tema_solo_"):
                self.tema_solo = acao.removeprefix("tema_solo_")
            self.partida = Partida(TEMAS[self.tema_solo]["perguntas"])
            self.navegar("pergunta")
        elif acao == "dica" and self.tela_atual == "pergunta":
            self.partida.revelar_dica()
        elif acao.startswith("resposta_") and self.tela_atual == "pergunta":
            alternativa = int(acao.rsplit("_", 1)[1])
            if self.partida.responder(alternativa) is not None:
                self.navegar("feedback")
        elif acao == "continuar" and self.tela_atual == "feedback":
            self.partida.continuar()
            if self.partida.perdeu:
                self.navegar("derrota")
            elif self.partida.venceu:
                self.navegar("vitoria")
            else:
                self.navegar("pergunta")

    def atualizar_tempo(self):
        agora = monotonic()
        decorrido = agora - self.ultima_atualizacao
        self.ultima_atualizacao = agora
        if self.tela_atual == "pergunta":
            self.partida.atualizar_tempo(decorrido)

    def atualizar(self):
        self.atualizar_tempo()
        if self.tela_atual == "pergunta" and self.partida.tempo_esgotado:
            self.navegar("feedback")
        self.salas.atualizar()

    def desenhar(self):
        self.atualizar_resolucao()
        self.ui.iniciar_tela()
        if self.tela_atual in ("amigos", "sala"):
            self.salas.desenhar()
        else:
            self.visuais.desenhar()
        pergunta_sala = (self.tela_atual == "sala" and self.salas.estado["fase"] == "pergunta"
                         and not self.salas.estado["voce"]["respondeu"] and not self.salas.confirmando_saida)
        x_som = 224 if self.tela_atual == "pergunta" or pergunta_sala else 322
        self.ui.controle_som(self.musica.habilitada, (x_som, 42, 40, 44))

    def tratar_evento(self, evento):
        if evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN, pygame.KEYDOWN):
            self.musica.iniciar()
        if self.tela_atual == "amigos" and self.salas.tratar_texto(evento):
            return
        if evento.type == pygame.QUIT:
            self.rodando = False
        elif evento.type == pygame.VIDEORESIZE:
            if sys.platform != "emscripten":
                self.janela = pygame.display.set_mode((max(1, evento.w), max(1, evento.h)),
                                                     pygame.RESIZABLE)
                self.atualizar_resolucao()
        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            if not getattr(evento, "touch", False):
                self.executar_acao(self.ui.acao_clicada(self.posicao_logica(evento.pos)))
        elif evento.type == pygame.FINGERUP:
            largura, altura = self.janela.get_size()
            posicao = self.posicao_logica((evento.x * largura, evento.y * altura))
            self.executar_acao(self.ui.acao_clicada(posicao))
        elif evento.type == pygame.KEYDOWN:
            self.tratar_tecla(evento)

    def tratar_tecla(self, evento):
        if evento.key == pygame.K_m:
            self.executar_acao("alternar_musica")
        elif evento.key == pygame.K_ESCAPE:
            if self.tela_atual == "amigos" and self.salas.escolhendo_icone:
                self.salas.executar_acao("sala_usar_icone")
                return
            if self.tela_atual == "amigos" and self.salas.escolhendo_tema:
                self.salas.executar_acao("sala_voltar_temas")
                return
            if self.tela_atual == "sala":
                acao = "sala_ficar" if self.salas.confirmando_saida else "sala_sair"
                self.salas.executar_acao(acao)
                return
            destino = {
                "pergunta": "confirmar_saida", "confirmar_saida": "pergunta",
                "ajuda": "inicio", "temas": "inicio", "amigos": "inicio",
                "vitoria": "inicio", "derrota": "inicio",
            }.get(self.tela_atual)
            # Um feedback pendente precisa ser confirmado para liberar uma resposta.
            if self.tela_atual == "feedback":
                return
            if destino:
                self.navegar(destino)
        elif evento.key in (pygame.K_TAB, pygame.K_DOWN, pygame.K_UP):
            direcao = -1 if evento.key == pygame.K_UP or evento.mod & pygame.KMOD_SHIFT else 1
            self.ui.mover_foco(direcao)
        elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.executar_acao(self.ui.acao_focada())
        elif self.tela_atual == "pergunta" or (
                self.tela_atual == "sala" and self.salas.estado["fase"] == "pergunta"
                and not self.salas.confirmando_saida):
            atalhos = {
                pygame.K_a: 0, pygame.K_b: 1, pygame.K_c: 2, pygame.K_d: 3,
                pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3,
            }
            if evento.key in atalhos:
                self.executar_acao(f"resposta_{atalhos[evento.key]}")

    def apresentar(self):
        self.janela.fill(CORES["azul_escuro"])
        self.janela.blit(self.tela, self.area_jogo)
        pygame.display.flip()


async def main():
    jogo = Jogo()
    relogio = pygame.time.Clock()
    try:
        jogo.desenhar()
        jogo.apresentar()
        if sys.platform == "emscripten":
            platform.window.cognit_pronto()
        while jogo.rodando:
            jogo.atualizar()
            jogo.ui.mouse = jogo.posicao_logica(pygame.mouse.get_pos())
            jogo.desenhar()
            # Uma ação por quadro evita que cliques/toques duplicados pulem o feedback.
            for evento in pygame.event.get():
                tela_anterior = jogo.tela_atual
                jogo.tratar_evento(evento)
                if jogo.tela_atual != tela_anterior:
                    break
            jogo.apresentar()
            if sys.platform != "emscripten":
                relogio.tick(FPS)
            # Necessário para o navegador executar o Pygame sem bloquear a página.
            await asyncio.sleep(0)
    finally:
        await jogo.salas.fechar()
        jogo.musica.encerrar()
        pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
