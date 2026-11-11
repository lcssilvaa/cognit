"""Telas de amigos e animações leves, desenhadas nas medidas de 390 × 844.

Nenhuma regra de pontos ou requisição HTTP fica aqui. O controlador informa
o instante de entrada em cada fase para as animações sobreviverem ao polling.
"""

from math import sin
from time import monotonic

import pygame

from avatares import AVATARES
from config import CORES, DURACAO_FEEDBACK_RODADA, MAX_JOGADORES
from telas_pergunta import desenhar_alternativas, desenhar_cabecalho, desenhar_dica, desenhar_enunciado
from visuais_temas import TEMAS_POR_PAGINA, desenhar_cartao_tema, desenhar_opcao_tema


def transicao(tempo, atraso=0, duracao=0.8):
    progresso = min(1, max(0, (tempo - atraso) / duracao))
    return 1 - (1 - progresso) ** 3


class VisuaisSala:
    def __init__(self, controlador):
        self.sala = controlador

    @property
    def ui(self):
        return self.sala.jogo.ui

    @property
    def estado(self):
        return self.sala.estado

    @property
    def tempo(self):
        return max(0, monotonic() - self.sala.fase_em)

    def desenhar(self):
        s = self.sala
        if s.jogo.tela_atual == "amigos":
            if s.escolhendo_icone:
                self._icones()
            elif s.escolhendo_tema:
                self._temas()
            else:
                self._formulario()
        elif s.confirmando_saida:
            self._saida()
        elif s.estado:
            fase = s.estado["fase"]
            if fase == "espera":
                self._lobby()
            elif fase == "pergunta":
                self._aguardando() if s.estado["voce"]["respondeu"] else self._pergunta()
            elif fase == "placar":
                if s.explicacao_visivel:
                    self._explicacao()
                elif s.painel_rodada == "feedback" and self.tempo < DURACAO_FEEDBACK_RODADA:
                    self._feedback()
                else:
                    self._ranking()
            else:
                self._podio()
        if s.jogo.tela_atual == "sala" and (s.erro_conexao or s.erro):
            self.ui.cartao((24, 93, 342, 34), "vermelho_claro", None, 10)
            self.ui.paragrafo(s.erro_conexao or s.erro, (32, 95, 326, 30), 13, "vermelho")

    def _topo(self, titulo):
        ui, e = self.ui, self.estado
        ui.botao("×", (24, 42, 44, 44), "sala_sair", "contorno", tamanho=25)
        ui.texto(f"SALA {e['codigo']}", (86, 44), 18, "azul", True)
        ui.paragrafo(e["nome_tema"], (86, 67, 220, 24), 14, "secundario")
        ui.texto(titulo, (24, 137), 28, negrito=True)

    def _formulario(self):
        ui, s = self.ui, self.sala
        ui.cabecalho("Jogar com amigos")
        for modo, rotulo, x in [("criar", "Criar sala", 24), ("entrar", "Entrar", 201)]:
            ui.botao(rotulo, (x, 181, 165, 44), "sala_modo_" + modo,
                     "azul" if s.modo == modo else "contorno", tamanho=17)
        ui.campo("Como você quer ser chamado?", s.campos["nome"], (24, 278, 342, 54),
                 "campo_nome", s.campo_ativo == "nome")
        ui.cartao((24, 358, 342, 108), "branco", None, 22)
        ui.avatar(s.icone, (38, 368, 86, 86))
        ui.texto("SEU CÉREBRO", (143, 374), 12, "secundario", True)
        ui.texto(AVATARES[s.icone]["nome"], (143, 394), 22, "azul_escuro", True)
        ui.texto("Personalizar  >", (143, 431), 15, "azul", True)
        ui.area_interativa((24, 358, 342, 108), "sala_escolher_icone")
        if s.modo == "criar":
            tema = next((t for t in s.temas if t["id"] == s.tema), None)
            ui.texto("Tema da sala", (24, 497), 15, "secundario", True)
            if tema:
                ui.botao("Alterar", (278, 485, 88, 32), "sala_escolher_tema", "contorno", tamanho=14)
                desenhar_cartao_tema(ui, tema, (24, 524, 342, 96),
                                    "sala_escolher_tema", compacto=True)
            else:
                ui.paragrafo("Conectando ao servidor…" if s.ocupado else "Nenhum tema disponível",
                             (24, 524, 342, 68), 18, "secundario")
            ui.botao("Criar minha sala", (24, 636, 342, 58), "sala_criar",
                     ativo=not s.ocupado and tema is not None)
            aviso = "Convide seus amigos pelo código da sala."
        else:
            ui.campo("Código da sala", s.campos["codigo"], (24, 524, 342, 64),
                     "campo_codigo", s.campo_ativo == "codigo")
            ui.botao("Vamos jogar", (24, 636, 342, 58), "sala_entrar", ativo=not s.ocupado)
            aviso = "Peça o código de 6 números a quem criou a sala."
        ui.paragrafo(s.erro or aviso, (32, 716, 326, 58), 16,
                     "vermelho" if s.erro else "secundario", centralizado=True)
        if s.erro and not s.ocupado:
            ui.texto("Tentar novamente", (195, 790), 15, "azul", True, True)
            ui.area_interativa((75, 779, 240, 42), "sala_reconectar")

    def _temas(self):
        """Seleciona diretamente no catálogo recebido do servidor, sem iniciar a sala."""
        ui, s = self.ui, self.sala
        ui.cabecalho("Escolha o tema", voltar="sala_voltar_temas")
        ui.paragrafo("O mesmo desafio para toda a turma.", (24, 156, 342, 38), 17, "secundario")
        ui.texto("TEMAS DISPONÍVEIS", (24, 206), 12, "secundario", True)
        ui.rotulo(f"{len(s.temas)} opções", (246, 200, 120, 28), 13, "secundario", centralizado=True)
        inicio = s.pagina_temas * TEMAS_POR_PAGINA
        for i, tema in enumerate(s.temas[inicio:inicio + TEMAS_POR_PAGINA]):
            selecionado = tema["id"] == s.tema
            desenhar_opcao_tema(ui, tema, (24, 244 + i * 226, 342, 210),
                                "sala_tema_" + tema["id"], selecionado)
        if len(s.temas) > TEMAS_POR_PAGINA:
            ui.botao("<", (24, 699, 48, 40), "sala_temas_anterior", "contorno", ativo=s.pagina_temas > 0)
            ui.texto(f"{s.pagina_temas + 1} / {(len(s.temas) - 1) // TEMAS_POR_PAGINA + 1}",
                     (195, 708), 16, "secundario", centralizado=True)
            ui.botao(">", (318, 699, 48, 40), "sala_temas_proxima", "contorno",
                     ativo=inicio + TEMAS_POR_PAGINA < len(s.temas))
        ui.paragrafo("Toque no cartão para escolher.\nDepois, é só criar a sala e convidar os amigos.",
                     (32, 754, 326, 57), 15, "secundario", centralizado=True)

    def _icones(self):
        ui, s = self.ui, self.sala
        ui.cabecalho("Escolha seu cérebro", voltar="sala_usar_icone")
        ui.texto("Um ícone para entrar no seu ritmo.", (24, 164), 17, "secundario")
        for i, (icone, cadastro) in enumerate(AVATARES.items()):
            x, y = 24 + i % 3 * 118, 223 + i // 3 * 146
            selecionado = icone == s.icone
            ui.cartao((x, y, 106, 130), "branco", "azul" if selecionado else None, 20)
            ui.avatar(icone, (x + 12, y + 8, 82, 82))
            ui.paragrafo(cadastro["nome"], (x + 4, y + 98, 98, 25), 15, "azul" if selecionado else "texto", True, True)
            ui.area_interativa((x, y, 106, 130), "sala_icone_" + icone)
            if selecionado:
                ui.circulo((x + 90, y + 15), 9, "verde")
                ui.simbolo_resultado(True, (x + 90, y + 15), 8)
        ui.avatar(s.icone, (135, 541 + sin(self.tempo * 3) * 4, 120, 120))
        ui.rotulo(s.campos["nome"] or "Esse é o seu estilo!", (24, 673, 342, 32), 21, "azul_escuro", True, True)
        ui.botao("Usar este ícone", (24, 752, 342, 56), "sala_usar_icone")

    def _bolinhas(self, y):
        for i in range(3):
            salto = max(0, sin(monotonic() * 4 - i * .7)) * 5
            self.ui.circulo((177 + i * 18, y - salto), 4, "azul")

    def _lobby(self):
        ui, e = self.ui, self.estado
        self._topo("Juntos no desafio")
        ui.avatar(e["voce"]["icone"], (147, 185 + sin(self.tempo * 2) * 4, 96, 96))
        ui.area_interativa((147, 181, 96, 100), "sala_pronto", not self.sala.ocupado)
        ui.texto("COMPARTILHE O CÓDIGO", (195, 294), 12, "secundario", True, True)
        codigo = e["codigo"]
        ui.texto(codigo[:3] + " " + codigo[3:], (195, 315), 42, "azul", True, True)
        prontos = sum(j["pronto"] and j["online"] for j in e["jogadores"])
        ui.texto(f"{len(e['jogadores'])}/{MAX_JOGADORES} jogadores · {prontos} pronto(s)",
                 (195, 373), 15, "secundario", centralizado=True)
        for i, jogador in enumerate(e["jogadores"]):
            x, y = 28 + i % 4 * 86, 408 + i // 4 * 81
            ui.avatar(jogador["icone"], (x + 8, y, 60, 60))
            ui.rotulo(jogador["nome"], (x, y + 60, 76, 21), 13, "azul" if jogador["id"] == e["voce"]["id"] else "texto", True, True)
            if jogador["pronto"]:
                ui.circulo((x + 62, y + 48), 8, "verde")
                ui.simbolo_resultado(True, (x + 62, y + 48), 7)
            elif not jogador["online"]:
                ui.circulo((x + 62, y + 48), 6, "desativado")
        self._bolinhas(683)
        mensagem = "Toque no seu cérebro para marcar que está pronto."
        if len(e["jogadores"]) < 2:
            mensagem = "Só falta um amigo para começar!"
        ui.paragrafo(mensagem, (32, 698, 326, 34), 15, "secundario", centralizado=True)
        if e["anfitriao"]:
            ui.botao("Começar a disputa", (24, 752, 342, 56), "sala_iniciar",
                     ativo=len(e["jogadores"]) >= 2 and not self.sala.ocupado)
        else:
            ui.botao("Tudo pronto!" if e["voce"]["pronto"] else "Estou pronto",
                     (24, 752, 342, 56), "sala_pronto",
                     "verde" if e["voce"]["pronto"] else "azul", ativo=not self.sala.ocupado)

    def _pergunta(self):
        ui, e, s = self.ui, self.estado, self.sala
        decorrido = max(0, monotonic() - s.recebido_em)
        restante = max(0, e["restante"] - decorrido)
        desenhar_cabecalho(ui, e["indice"], e["total"], e["nome_tema"],
                           restante, e["limite"], "sala_sair")
        desenhar_enunciado(ui, e["pergunta"])
        bloqueada = restante <= 0 or s.ocupado
        desenhar_alternativas(ui, e["pergunta"], bloqueadas=bloqueada)
        desenhar_dica(ui, max(0, e["espera_dica"] - decorrido), e.get("dica"), not bloqueada)

    def _aguardando(self):
        ui, e = self.ui, self.estado
        self._topo(f"Pergunta {e['indice'] + 1} de {e['total']}")
        ui.avatar(e["voce"]["icone"], (125, 217 + sin(self.tempo * 3) * 6, 140, 140))
        ui.texto("Resposta enviada!", (195, 390), 29, "azul_escuro", True, True)
        self._bolinhas(456)
        ui.paragrafo("Agora é com a turma. O resultado aparece quando a rodada terminar.",
                     (42, 486, 306, 72), 19, "secundario", centralizado=True)
        ui.cartao((105, 584, 180, 44), "azul_claro", None, 18)
        ui.texto(f"Você escolheu {chr(65 + e['voce']['alternativa'])}", (195, 596), 16, "azul", True, True)
        ui.texto(f"{e['respondidos']} de {len(e['jogadores'])} responderam", (195, 664), 17, "azul", True, True)
        ui.progresso(e["respondidos"] / len(e["jogadores"]) * 100, (70, 705, 250, 8))

    def _confetes(self, tempo):
        for i in range(32):
            x = (i * 79 + sin(tempo * 2 + i) * 16) % 390
            y = (i * 97 + tempo * (50 + i % 5 * 12)) % 900 - 50
            cor = ["amarelo", "roxo", "verde", "azul"][i % 4]
            pygame.draw.rect(self.ui.tela, CORES[cor], self.ui.retangulo((x, y, 4, 7)), border_radius=1)

    def _feedback(self):
        ui, e, t = self.ui, self.estado, self.tempo
        voce = e["voce"]
        acertou = voce["resultado"] == "acertou"
        cor = "verde" if acertou else "vermelho"
        self._topo("Resultado da rodada")
        if acertou:
            self._confetes(t)
        ui.cartao((24, 194, 342, 326), f"{cor}_claro", None, 28)
        ui.avatar(voce["icone"], (147, 205 + sin(t * 4) * 3, 96, 96))
        ui.circulo((195, 326), 26, cor)
        ui.simbolo_resultado(acertou, (195, 326), 25)
        titulo = {"acertou": "Acertou!", "errou": "Errou!", "sem_resposta": "Tempo esgotado!"}[voce["resultado"]]
        ui.texto(titulo, (195, 365), 33, cor, True, True)
        ui.cartao((58, 425, 274, 72), "branco", None, 20)
        ganho = round(voce["ganho"] * transicao(t, .1, 1))
        ui.texto(f"+ {ganho}", (195, 428), 43, cor, True, True)
        ui.texto("pontos nesta rodada", (195, 479), 12, "secundario", centralizado=True)
        self._posicao_pessoal(548)
        correta = e["pergunta"]["alternativas"][e["correta"]]
        ui.paragrafo("Resposta: " + correta, (32, 645, 326, 42), 17, "verde", True, True)
        mensagem = f"{voce['sequencia']} acertos seguidos!" if voce["sequencia"] > 1 else "Cada rodada é uma nova chance."
        ui.texto(mensagem, (195, 704), 15, "secundario", centralizado=True)
        ui.botao("Ver classificação", (24, 752, 342, 56), "sala_ver_placar", cor)

    def _posicao_pessoal(self, y):
        ui, voce = self.ui, self.estado["voce"]
        ui.cartao((24, y, 342, 70), "branco", "azul", 20)
        ui.texto(f"{voce['posicao']}º", (44, y + 12), 31, "azul", True)
        ui.texto("SUA POSIÇÃO", (112, y + 12), 12, "secundario", True)
        movimento = voce["movimento"]
        mensagem = f"Subiu {movimento} posição(ões)!" if movimento > 0 else f"{voce['pontos']} pontos no total"
        ui.texto(mensagem, (112, y + 35), 16, "azul_escuro", True)

    def _linha_ranking(self, jogador, y):
        ui, e = self.ui, self.estado
        posicao = jogador["posicao"]
        fundo = {1: "amarelo_claro", 2: "azul_claro", 3: "roxo_claro"}.get(posicao, "branco")
        voce = jogador["id"] == e["voce"]["id"]
        ui.cartao((24, y, 342, 64), fundo, "azul" if voce else None, 18)
        ui.texto(str(posicao), (44, y + 18), 23, "azul_escuro", True)
        ui.avatar(jogador["icone"], (68, y + 7, 50, 50))
        ui.rotulo(jogador["nome"], (130, y + 8, 144, 28), 17, "azul_escuro", True)
        ui.texto("VOCÊ" if voce else f"{jogador['acertos']} acerto(s)", (130, y + 39), 11, "azul" if voce else "secundario", voce)
        ui.rotulo(str(jogador["pontos"]), (280, y + 12, 74, 40), 18, "azul_escuro", True, True)

    def _ranking(self):
        ui, e = self.ui, self.estado
        self._topo("Classificação")
        ui.texto(f"TOP 5 · RODADA {e['indice'] + 1}", (24, 190), 13, "secundario", True)
        ui.paragrafo("Ver explicação", (220, 182, 146, 30), 13, "azul", True, True)
        ui.area_interativa((220, 180, 146, 34), "sala_ver_explicacao")
        for i, jogador in enumerate(e["jogadores"][:5]):
            self._linha_ranking(jogador, 225 + i * 72)
        self._posicao_pessoal(606)
        ui.texto("Ver minha resposta", (195, 705), 15, "azul", True, True)
        ui.area_interativa((70, 693, 250, 40), "sala_ver_resposta")
        if e["anfitriao"]:
            rotulo = "Revelar o pódio" if e["indice"] + 1 == e["total"] else "Próxima pergunta"
            ui.botao(rotulo, (24, 752, 342, 56), "sala_proxima", ativo=not self.sala.ocupado)
        else:
            self._bolinhas(773)
            ui.texto("Aguardando o anfitrião", (195, 800), 14, "secundario", centralizado=True)

    def _explicacao(self):
        ui, e = self.ui, self.estado
        self._topo("Entenda a resposta")
        correta = e["pergunta"]["alternativas"][e["correta"]]
        ui.cartao((24, 224, 342, 362), "branco", None, 24)
        ui.texto("RESPOSTA CORRETA", (44, 246), 13, "verde", True)
        ui.paragrafo(correta, (44, 282, 302, 100), 25, "verde", True)
        ui.paragrafo(e["explicacao"], (44, 406, 302, 152), 21, "texto")
        ui.botao("Voltar à classificação", (24, 752, 342, 56), "sala_ver_placar")

    def _podio(self):
        ui, e, t = self.ui, self.estado, self.tempo
        self._topo("O pódio é de vocês!")
        self._confetes(t)
        empatados = sum((j["pontos"], j["acertos"]) == (e["jogadores"][0]["pontos"], e["jogadores"][0]["acertos"]) for j in e["jogadores"])
        ui.texto("Vitória compartilhada!" if empatados > 1 else "Valeu cada desafio.",
                 (195, 186), 17, "secundario", centralizado=True)
        for indice, x, altura, atraso, cor in [(1, 28, 145, .45, "azul"), (2, 260, 115, 0, "roxo"), (0, 144, 190, .9, "amarelo")]:
            if indice >= len(e["jogadores"]):
                continue
            jogador = e["jogadores"][indice]
            progresso = transicao(t, atraso, .9)
            if progresso <= 0:
                continue
            topo = 544 - altura * progresso
            ui.cartao((x, topo, 102, altura * progresso), cor, None, 16)
            tamanho = 76 if indice == 0 else 66
            ui.avatar(jogador["icone"], (x + (102 - tamanho) / 2, topo - 116 + sin(t * 3 + indice) * 3, tamanho, tamanho))
            ui.rotulo(jogador["nome"], (x - 4, topo - 44, 110, 38), 16, "azul_escuro", True, True)
            texto = "azul_escuro" if indice == 0 else "branco"
            ui.texto(str(jogador["posicao"]), (x + 51, topo + 15), 32, texto, True, True)
            if altura * progresso > 85:
                ui.texto(str(jogador["pontos"]), (x + 51, topo + 65), 18, texto, True, True)
                ui.texto("pontos", (x + 51, topo + 89), 12, texto, centralizado=True)
            ui.area_interativa((x, topo - 120, 102, altura * progresso + 120), "sala_podio_" + jogador["id"])
        for i, jogador in enumerate(e["jogadores"][3:5]):
            x = 24 + i * 177
            ui.cartao((x, 570, 165, 48), "branco", None, 14)
            ui.avatar(jogador["icone"], (x + 6, 576, 36, 36))
            ui.rotulo(f"{jogador['posicao']}º {jogador['nome']}", (x + 47, 575, 112, 36), 14, "azul_escuro", True)
            ui.area_interativa((x, 570, 165, 48), "sala_podio_" + jogador["id"])
        selecionado = next((j for j in e["jogadores"] if j["id"] == self.sala.detalhe_podio), None)
        if selecionado:
            ui.paragrafo(f"{selecionado['nome']} · {selecionado['pontos']} pontos\n{selecionado['acertos']} de {e['total']} acertos",
                         (28, 632, 334, 54), 17, "azul_escuro", True, True)
        else:
            ui.paragrafo("Toque em um cérebro para ver seu desempenho.", (36, 634, 318, 48), 16, "secundario", centralizado=True)
        ui.texto(f"Você ficou em {e['voce']['posicao']}º · {e['voce']['pontos']} pontos", (195, 710), 17, "azul", True, True)
        ui.botao("Rever pódio", (24, 756, 156, 52), "sala_rever_podio", "contorno", tamanho=16)
        ui.botao("Sair da sala", (193, 756, 173, 52), "sala_confirmar_saida", tamanho=17)

    def _saida(self):
        ui = self.ui
        ui.avatar(self.estado["voce"]["icone"], (125, 167, 140, 140))
        ui.texto("Sair da sala?", (195, 350), 30, "azul_escuro", True, True)
        ui.paragrafo("Sua pontuação será removida. Se você for o anfitrião, outro jogador assume a sala.",
                     (36, 410, 318, 100), 20, "secundario", centralizado=True)
        ui.botao("Continuar na sala", (32, 551, 326, 58), "sala_ficar", ativo=not self.sala.saindo)
        ui.botao("Sair da sala", (32, 628, 326, 56), "sala_confirmar_saida", "contorno", ativo=not self.sala.saindo)
