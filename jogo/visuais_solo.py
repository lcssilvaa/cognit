"""Desenhos do modo solo, separados dos eventos e das regras do quiz.

As posições usam as medidas do protótipo. Interface adapta o desenho à janela.
"""

from config import ESPERA_DICA, TEMPO_INICIAL, TITULO
from telas_pergunta import desenhar_alternativas, desenhar_cabecalho, desenhar_dica, desenhar_enunciado
from temas import TEMAS, catalogo_temas
from visuais_temas import TEMAS_POR_PAGINA, desenhar_cartao_tema


class VisuaisSolo:
    def __init__(self, jogo):
        self.jogo = jogo

    @property
    def ui(self):
        return self.jogo.ui

    @property
    def partida(self):
        return self.jogo.partida

    def desenhar(self):
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
        telas[self.jogo.tela_atual]()

    def desenhar_inicio(self):
        ui = self.ui
        ui.ilustracao("marca.svg", (117, 126, 156, 156))
        ui.texto(TITULO.lower(), (195, 316), 66, "azul_escuro", True, True)
        ui.paragrafo("Teste sua mente.\nSupere seus limites.", (35, 412, 320, 65),
                      21, "secundario", centralizado=True)
        ui.botao("Jogar sozinho", (32, 518, 326, 58), "temas")
        ui.botao("Jogar com amigos", (32, 591, 326, 58), "amigos")
        ui.botao("Como jogar", (32, 664, 326, 54), "ajuda", "contorno")
        ui.vidas(self.partida.vidas_iniciais, self.partida.vidas_iniciais, y=774)

    def desenhar_temas(self):
        ui = self.ui
        ui.cabecalho("Escolha seu tema")
        ui.paragrafo("Um novo conhecimento a cada nível.", (24, 159, 342, 42),
                      17, "secundario")
        temas = catalogo_temas()
        inicio = self.jogo.pagina_temas * TEMAS_POR_PAGINA
        for i, tema in enumerate(temas[inicio:inicio + TEMAS_POR_PAGINA]):
            desenhar_cartao_tema(ui, tema, (24, 224 + i * 208, 342, 190), "tema_solo_" + tema["id"])
        if len(temas) > TEMAS_POR_PAGINA:
            ui.botao("<", (24, 654, 48, 40), "temas_anterior", "contorno", ativo=self.jogo.pagina_temas > 0)
            ui.texto(f"{self.jogo.pagina_temas + 1} / {(len(temas) - 1) // TEMAS_POR_PAGINA + 1}",
                     (195, 663), 16, "secundario", centralizado=True)
            ui.botao(">", (318, 654, 48, 40), "temas_proxima", "contorno", ativo=inicio + TEMAS_POR_PAGINA < len(temas))
        ui.mascote("feliz", (29, 737, 76, 64))
        ui.paragrafo("Vamos aprender juntos?", (118, 739, 240, 57),
                      17, "azul", True)

    def desenhar_ajuda(self):
        ui = self.ui
        ui.cabecalho("Como jogar")
        ui.mascote("feliz", (122, 180, 146, 120))
        regras = [
            ("01", "Escolha seu tema", "Os temas cadastrados aparecem no menu. As perguntas seguem a ordem de dificuldade."),
            ("02", "Observe o relógio", f"Começa em {TEMPO_INICIAL} s e diminui por nível. O tempo esgotado custa uma vida."),
            ("03", f"Cuide das suas {self.partida.vidas_iniciais} vidas",
             "Um erro custa uma vida. Tente outra alternativa na mesma pergunta."),
            ("04", "Peça ajuda ao cérebro", f"Após {ESPERA_DICA} segundos, toque no mascote para ler uma pequena dica."),
        ]
        for i, (numero, titulo, descricao) in enumerate(regras):
            y = 320 + i * 88
            ui.texto(numero, (28, y + 2), 23, "azul", True)
            ui.texto(titulo, (76, y), 19, negrito=True)
            ui.paragrafo(descricao, (76, y + 27, 283, 53), 16, "secundario")
        ui.botao("Vamos jogar", (32, 701, 326, 56), "temas")

    def desenhar_pergunta(self):
        ui, partida = self.ui, self.partida
        pergunta = partida.pergunta
        desenhar_cabecalho(ui, partida.indice, len(partida.perguntas),
                           TEMAS[self.jogo.tema_solo]["nome"], partida.tempo_restante,
                           partida.tempo_limite, "confirmar_saida")
        ui.vidas(partida.vidas, partida.vidas_iniciais, centro_x=330, y=121, tamanho=14)
        desenhar_enunciado(ui, pergunta)
        desenhar_alternativas(ui, pergunta, partida.alternativas_erradas)
        desenhar_dica(ui, partida.espera_dica,
                      pergunta.get("dica") if partida.dica_visivel else None,
                      tem_dica=bool(pergunta.get("dica")))

    def desenhar_feedback(self):
        ui, partida = self.ui, self.partida
        acertou = partida.ultimo_acerto
        cor = "verde" if acertou else "vermelho"
        ui.mascote("feliz" if acertou else "triste", (86, 109, 218, 182))
        titulo = "Acertou!" if acertou else "Tempo esgotado!" if partida.tempo_esgotado else "Errou!"
        ui.texto(titulo, (195, 321),
                 43, cor, True, True)
        if acertou:
            mensagem = partida.pergunta["explicacao"]
        elif partida.perdeu:
            mensagem = "Suas vidas acabaram. Todo aprendizado começa com uma tentativa!"
        else:
            restante = "Resta 1 vida." if partida.vidas == 1 else f"Restam {partida.vidas} vidas."
            if partida.tempo_esgotado:
                mensagem = f"O prazo acabou e você perdeu uma vida. {restante}\nTente a pergunta com um novo prazo."
            else:
                mensagem = f"Você perdeu uma vida. {restante}\nTente outra alternativa com o tempo restante."
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
        venceu = self.jogo.tela_atual == "vitoria"
        cor = "azul" if venceu else "vermelho"
        if venceu:
            for x, y in [(38, 136), (337, 204), (59, 305), (319, 104)]:
                ui.circulo((x, y), 5, "amarelo")
        ui.mascote("feliz" if venceu else "triste", (79, 133, 232, 191))
        ui.texto("Parabéns!" if venceu else "Game Over", (195, 351),
                 43, cor, True, True)
        ui.texto("Você completou o Cognit." if venceu else "Suas vidas acabaram.",
                 (195, 417), 20, "secundario", centralizado=True)
        ui.cartao((47, 477, 296, 164))
        ui.texto("Desafio concluído" if venceu else "Seu progresso", (195, 491),
                 17, "secundario", centralizado=True)
        ui.texto(f"{partida.progresso}%", (195, 515), 44, "verde" if venceu else "azul", True, True)
        ui.progresso(partida.progresso, (71, 584, 248, 10), "verde" if venceu else "azul")
        ui.texto(f"{partida.acertos} de {len(partida.perguntas)} perguntas · {partida.erros} erro(s)",
                 (195, 612), 15, "secundario", centralizado=True)
        ui.vidas(partida.vidas, partida.vidas_iniciais, y=671)
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
