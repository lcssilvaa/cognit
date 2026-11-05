"""Cognit: navegação entre telas e loop principal em Pygame.

Execute a partir da raiz: python jogo/main.py
Perguntas: perguntas.py | Cores e vidas: config.py | Regras: partida.py
"""

import asyncio
import platform
import sys

import pygame

from config import ALTURA, CORES, FPS, LARGURA, TITULO
from interface import Interface
from partida import Partida


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
        self.tela_atual = "inicio"
        self.rodando = True

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
        self.tela_atual = tela
        self.ui.foco = 0
        self.ui.foco_ativo = False
        # Descarta botões da tela anterior antes do próximo evento.
        self.ui.botoes = []

    def executar_acao(self, acao):
        if acao is None:
            return
        if acao in ("inicio", "temas", "ajuda", "confirmar_saida", "pergunta"):
            self.navegar(acao)
        elif acao == "jogar":
            self.partida = Partida()
            self.navegar("pergunta")
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

    def desenhar(self):
        self.atualizar_resolucao()
        self.ui.iniciar_tela()
        telas = {
            "inicio": self.desenhar_inicio,
            "temas": self.desenhar_temas,
            "ajuda": self.desenhar_ajuda,
            "pergunta": self.desenhar_pergunta,
            "feedback": self.desenhar_feedback,
            "vitoria": self.desenhar_resultado,
            "derrota": self.desenhar_resultado,
            "confirmar_saida": self.desenhar_saida,
        }
        telas[self.tela_atual]()

    def desenhar_inicio(self):
        ui = self.ui
        ui.ilustracao("marca.svg", (117, 126, 156, 156))
        ui.texto(TITULO.lower(), (195, 316), 66, "azul_escuro", True, True)
        ui.paragrafo("Teste sua mente.\nSupere seus limites.", (35, 412, 320, 65),
                      21, "secundario", centralizado=True)
        ui.botao("Iniciar", (32, 536, 326, 60), "temas")
        ui.botao("Como jogar", (32, 610, 326, 58), "ajuda", "contorno")
        ui.vidas(self.partida.vidas_iniciais, self.partida.vidas_iniciais, y=732)
        ui.texto(f"{self.partida.vidas_iniciais} vidas  ·  {len(self.partida.perguntas)} perguntas  ·  Tecnologia",
                 (195, 774), 15, "secundario", centralizado=True)

    def cabecalho(self, titulo, voltar="inicio"):
        self.ui.botao("<", (24, 42, 44, 44), voltar, "contorno", tamanho=24)
        self.ui.texto(titulo, (24, 114), 29, negrito=True)

    def desenhar_temas(self):
        ui = self.ui
        self.cabecalho("Escolha seu tema")
        ui.paragrafo("Um novo conhecimento a cada nível.", (24, 159, 342, 42),
                      17, "secundario")
        ui.cartao((24, 224, 342, 213), "azul", None)
        ui.texto("</>", (47, 240), 37, "branco", True)
        ui.texto("Tecnologia", (47, 296), 27, "branco", True)
        ui.texto(f"{len(self.partida.perguntas)} perguntas · dificuldade crescente", (47, 339),
                 16, "branco")
        ui.botao("Jogar agora", (45, 373, 300, 48), "jogar", "contorno", tamanho=18)
        for y, nome, simbolo in [(463, "Conhecimentos gerais", "?"), (587, "Ciência", "+")]:
            ui.cartao((24, y, 342, 102), "azul_claro")
            ui.texto(simbolo, (45, y + 23), 30, "desativado", True)
            ui.texto(nome, (91, y + 20), 20, "secundario", True)
            ui.texto("Em breve", (91, y + 52), 16, "secundario")
        ui.mascote("feliz", (29, 737, 76, 64))
        ui.paragrafo("Vamos aprender juntos?", (118, 739, 240, 57),
                      17, "azul", True)

    def desenhar_ajuda(self):
        ui = self.ui
        self.cabecalho("Como jogar")
        ui.mascote("feliz", (122, 180, 146, 120))
        regras = [
            ("01", "Escolha Tecnologia", "São cinco perguntas em ordem de dificuldade."),
            ("02", "Responda com calma", "Cada acerto libera a pergunta do próximo nível."),
            ("03", f"Cuide das suas {self.partida.vidas_iniciais} vidas",
             "Um erro custa uma vida. Tente outra alternativa na mesma pergunta."),
            ("04", "Conclua o desafio", "Acerte todas para vencer. Sem vidas, a partida termina."),
        ]
        for i, (numero, titulo, descricao) in enumerate(regras):
            y = 320 + i * 88
            ui.texto(numero, (28, y + 2), 23, "azul", True)
            ui.texto(titulo, (76, y), 19, negrito=True)
            ui.paragrafo(descricao, (76, y + 27, 283, 53), 16, "secundario")
        ui.botao("Vamos jogar", (32, 701, 326, 56), "temas")
        ui.texto("Mouse/toque · Tab e Enter · A, B, C ou D", (195, 785),
                 13, "secundario", centralizado=True)

    def desenhar_pergunta(self):
        ui, partida = self.ui, self.partida
        pergunta = partida.pergunta
        ui.botao("×", (24, 42, 44, 44), "confirmar_saida", "contorno", tamanho=25)
        ui.vidas(partida.vidas, partida.vidas_iniciais, centro_x=303, y=61, tamanho=24)
        ui.progresso(partida.progresso, (24, 112, 292, 12))
        ui.texto(f"{partida.progresso}%", (328, 104), 16, "azul", True)
        ui.cartao((24, 145, 106, 28), "roxo_claro", None, 14)
        ui.texto("Tecnologia", (77, 149), 14, "roxo", True, True)
        ui.texto(f"Nível {partida.indice + 1} de {len(partida.perguntas)}", (251, 150),
                 14, "secundario")
        ui.texto(pergunta["dificuldade"], (26, 187), 16, "azul", True)
        ui.cartao((24, 220, 342, 198))
        if pergunta.get("codigo"):
            ui.paragrafo(pergunta["enunciado"], (44, 233, 303, 65), 23, negrito=True)
            ui.cartao((42, 310, 306, 89), "azul_escuro", None, 14)
            ui.paragrafo(pergunta["codigo"], (56, 319, 278, 70), 18, "branco")
        else:
            ui.paragrafo(pergunta["enunciado"], (47, 238, 296, 162), 26, negrito=True)
        for i, alternativa in enumerate(pergunta["alternativas"]):
            # O quarto espaço também funciona ao personalizar uma pergunta com 4 opções.
            ui.alternativa(i, alternativa, (24, 440 + i * 73, 342, 62),
                           i in partida.alternativas_erradas)
        ui.mascote("pensativo", (22, 753, 84, 70))
        ui.cartao((118, 750, 248, 69), raio=18)
        aviso = "Última vida! Leia com calma." if partida.vidas == 1 else "Pense com calma. Você consegue!"
        ui.paragrafo(aviso, (136, 758, 212, 52), 16, "azul", True)

    def desenhar_feedback(self):
        ui, partida = self.ui, self.partida
        acertou = partida.ultimo_acerto
        cor = "verde" if acertou else "vermelho"
        ui.mascote("feliz" if acertou else "triste", (86, 109, 218, 182))
        ui.texto("Acertou!" if acertou else "Errou!", (195, 321),
                 43, cor, True, True)
        if acertou:
            mensagem = partida.pergunta["explicacao"]
        elif partida.perdeu:
            mensagem = "Suas vidas acabaram. Todo aprendizado começa com uma tentativa!"
        else:
            restante = "Resta 1 vida." if partida.vidas == 1 else f"Restam {partida.vidas} vidas."
            mensagem = f"Você perdeu uma vida. {restante}\nTente outra alternativa na mesma pergunta."
        ui.cartao((24, 402, 342, 129), f"{cor}_claro", None)
        ui.paragrafo(mensagem, (43, 414, 304, 105), 19, "texto", centralizado=True)
        ui.texto(f"Progresso: {partida.progresso}%", (195, 557), 20, "azul", True, True)
        ui.progresso(partida.progresso, (52, 600, 286, 12), cor)
        ui.vidas(partida.vidas, partida.vidas_iniciais, y=655)
        rotulo = "Próxima pergunta" if acertou else "Tentar outra resposta"
        if partida.venceu or partida.perdeu:
            rotulo = "Ver resultado"
        ui.botao(rotulo, (32, 735, 326, 60), "continuar", cor)

    def desenhar_resultado(self):
        ui, partida = self.ui, self.partida
        venceu = self.tela_atual == "vitoria"
        cor = "azul" if venceu else "vermelho"
        if venceu:
            for x, y in [(38, 136), (337, 204), (59, 305), (319, 104)]:
                ui.circulo((x, y), 5, "amarelo")
        ui.mascote("feliz" if venceu else "triste", (79, 133, 232, 191))
        ui.texto("Parabéns!" if venceu else "Game Over", (195, 351),
                 43, cor, True, True)
        ui.texto("Você completou o Cognit." if venceu else "Suas vidas acabaram.",
                 (195, 417), 20, "secundario", centralizado=True)
        ui.cartao((47, 477, 296, 130))
        ui.texto("Desafio concluído" if venceu else "Seu progresso", (195, 491),
                 17, "secundario", centralizado=True)
        ui.texto(f"{partida.progresso}%", (195, 515), 44, "verde" if venceu else "azul", True, True)
        ui.texto(f"{partida.acertos} de {len(partida.perguntas)} perguntas · {partida.erros} erro(s)",
                 (195, 574), 15, "secundario", centralizado=True)
        ui.vidas(partida.vidas, partida.vidas_iniciais, y=643)
        ui.botao("Jogar novamente" if venceu else "Tentar de novo", (32, 706, 326, 58), "jogar")
        ui.botao("Menu inicial", (32, 780, 326, 44), "inicio", "contorno", tamanho=18)

    def desenhar_saida(self):
        ui = self.ui
        ui.mascote("pensativo", (112, 167, 166, 140))
        ui.texto("Sair da partida?", (195, 350), 30, "azul_escuro", True, True)
        ui.paragrafo("Ao voltar aos temas, esta partida será encerrada.",
                      (44, 411, 302, 90), 21, "secundario", centralizado=True)
        ui.botao("Continuar jogando", (32, 551, 326, 58), "pergunta")
        ui.botao("Voltar aos temas", (32, 628, 326, 56), "temas", "contorno")

    def tratar_evento(self, evento):
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
        if evento.key == pygame.K_ESCAPE:
            destino = {
                "pergunta": "confirmar_saida", "confirmar_saida": "pergunta",
                "ajuda": "inicio", "temas": "inicio",
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
        elif self.tela_atual == "pergunta":
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
    jogo.desenhar()
    jogo.apresentar()
    if sys.platform == "emscripten":
        platform.window.cognit_pronto()
    while jogo.rodando:
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
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
