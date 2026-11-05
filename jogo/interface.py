"""Peças visuais reutilizáveis: texto, cartões, botões, vidas e imagens."""

from functools import lru_cache
from pathlib import Path

import pygame

from config import CORES, LARGURA

ASSETS = Path(__file__).resolve().parent / "assets"


class Interface:
    def __init__(self, tela):
        self.botoes = []
        self.foco = 0
        self.foco_ativo = False
        self.mouse = (-1, -1)
        self.redimensionar(tela)

    def redimensionar(self, tela):
        """Desenha na resolução real, mantendo as coordenadas do protótipo."""
        self.tela = tela
        self.escala = tela.get_width() / LARGURA
        self.fonte.cache_clear()
        self.imagem.cache_clear()
        self.fundo = pygame.Surface(tela.get_size())
        inicio = pygame.Color(CORES["fundo_inicio"])
        fim = pygame.Color(CORES["fundo_fim"])
        largura, altura = tela.get_size()
        for y in range(altura):
            cor = inicio.lerp(fim, y / max(1, altura - 1))
            pygame.draw.line(self.fundo, cor, (0, y), (largura, y))

    def medida(self, valor):
        return round(valor * self.escala)

    def ponto(self, posicao):
        return tuple(self.medida(valor) for valor in posicao)

    def retangulo(self, area):
        area = pygame.Rect(area)
        return pygame.Rect(self.ponto(area.topleft), self.ponto(area.size))

    def contorno(self, area, cor, raio=20):
        pygame.draw.rect(self.tela, CORES[cor], self.retangulo(area),
                         max(1, self.medida(2)), border_radius=self.medida(raio))

    def circulo(self, posicao, raio, cor):
        pygame.draw.circle(self.tela, CORES[cor], self.ponto(posicao),
                           max(1, self.medida(raio)))

    @lru_cache(maxsize=80)
    def fonte(self, tamanho, negrito=False):
        arquivo = "Nunito-Bold.ttf" if negrito else "Nunito-Regular.ttf"
        return pygame.font.Font(str(ASSETS / arquivo), max(1, self.medida(tamanho)))

    @lru_cache(maxsize=32)
    def imagem(self, nome, largura, altura):
        caminho = ASSETS / nome
        tamanho = self.ponto((largura, altura))
        if caminho.suffix == ".svg":
            if caminho.is_file():
                return pygame.image.load_sized_svg(str(caminho), tamanho).convert_alpha()
            caminho = caminho.with_suffix(".png")
        original = pygame.image.load(str(caminho)).convert_alpha()
        return pygame.transform.smoothscale(original, tamanho)

    def ilustracao(self, nome, area):
        area = pygame.Rect(area)
        self.tela.blit(self.imagem(nome, *area.size), self.ponto(area.topleft))

    def iniciar_tela(self):
        self.botoes = []
        self.tela.blit(self.fundo, (0, 0))

    def texto(self, texto, posicao, tamanho=20, cor="texto", negrito=False,
              centralizado=False):
        imagem = self.fonte(tamanho, negrito).render(str(texto), True, CORES[cor])
        retangulo = imagem.get_rect()
        if centralizado:
            retangulo.midtop = self.ponto(posicao)
        else:
            retangulo.topleft = self.ponto(posicao)
        self.tela.blit(imagem, retangulo)
        return retangulo

    def linhas(self, texto, fonte, largura):
        """Quebra o texto pelo espaço disponível, respeitando as quebras manuais."""
        linhas = []
        for trecho in texto.split("\n"):
            linha = ""
            for palavra in trecho.split():
                teste = f"{linha} {palavra}".strip()
                if linha and fonte.size(teste)[0] > largura:
                    linhas.append(linha)
                    linha = palavra
                else:
                    linha = teste
            linhas.append(linha)
        return linhas

    def paragrafo(self, texto, area, tamanho=20, cor="texto", negrito=False,
                  centralizado=False):
        """Reduz a fonte quando necessário para caber na área do cartão."""
        area = self.retangulo(area)
        while True:
            fonte = self.fonte(tamanho, negrito)
            linhas = self.linhas(texto, fonte, area.width)
            passo = fonte.get_linesize() + self.medida(2)
            if len(linhas) * passo <= area.height or tamanho <= 12:
                break
            tamanho -= 1
        y = area.y + (area.height - len(linhas) * passo) // 2
        for linha in linhas:
            imagem = fonte.render(linha, True, CORES[cor])
            x = area.centerx - imagem.get_width() // 2 if centralizado else area.x
            self.tela.blit(imagem, (x, y))
            y += passo

    def cartao(self, area, cor="branco", borda="borda", raio=24):
        area = self.retangulo(area)
        pygame.draw.rect(self.tela, CORES[cor], area, border_radius=self.medida(raio))
        if borda:
            pygame.draw.rect(self.tela, CORES[borda], area, width=max(1, self.medida(2)),
                             border_radius=self.medida(raio))

    def botao(self, rotulo, area, acao, estilo="azul", ativo=True, tamanho=20):
        """Registra a ação do botão. O main.py decide o que ela faz."""
        area = pygame.Rect(area)
        contorno = estilo == "contorno"
        fundo = "branco" if contorno else estilo
        cor_texto = "azul" if contorno else "branco"
        borda = "azul" if contorno else None
        if not ativo:
            fundo, cor_texto, borda = "azul_claro", "desativado", "borda"
        self.cartao(area, fundo, borda, raio=area.height // 2)
        if ativo:
            self.botoes.append((area, acao))
            destaque = area.collidepoint(self.mouse) or (
                self.foco_ativo and self.foco == len(self.botoes) - 1)
            if destaque:
                self.contorno(area.inflate(6, 6), "azul_escuro", area.height // 2 + 3)
        self.paragrafo(rotulo, area.inflate(-24, -8), tamanho, cor_texto,
                       negrito=True, centralizado=True)

    def alternativa(self, indice, rotulo, area, desativada=False):
        area = pygame.Rect(area)
        self.cartao(area, "azul_claro" if desativada else "branco", raio=20)
        cor = "desativado" if desativada else "azul"
        circulo = (area.x + 34, area.centery)
        self.circulo(circulo, 18, "borda" if desativada else "azul_claro")
        self.texto(chr(65 + indice), (circulo[0], circulo[1] - 14),
                   19, cor, True, True)
        self.paragrafo(rotulo, (area.x + 66, area.y + 5, area.width - 83, area.height - 10),
                       19, "desativado" if desativada else "texto", True)
        if not desativada:
            self.botoes.append((area, f"resposta_{indice}"))
            if area.collidepoint(self.mouse) or (
                    self.foco_ativo and self.foco == len(self.botoes) - 1):
                self.contorno(area, "azul")

    def vidas(self, quantidade, total, centro_x=195, y=80, tamanho=26):
        espacamento = tamanho + 11
        inicio = centro_x - (total - 1) * espacamento / 2
        for i in range(total):
            x = inicio + i * espacamento
            cor = "vermelho" if i < quantidade else "borda"
            # Um coração é formado por dois círculos e um triângulo.
            raio = tamanho // 4
            self.circulo((x - raio, y), raio, cor)
            self.circulo((x + raio, y), raio, cor)
            pygame.draw.polygon(self.tela, CORES[cor], [
                self.ponto((x - 2 * raio, y + 2)),
                self.ponto((x + 2 * raio, y + 2)),
                self.ponto((x, y + 2 * raio + 3)),
            ])

    def progresso(self, percentual, area, cor="azul"):
        area = self.retangulo(area)
        pygame.draw.rect(self.tela, CORES["borda"], area, border_radius=self.medida(8))
        if percentual > 0:
            preenchido = area.copy()
            preenchido.width = max(self.medida(8), round(area.width * percentual / 100))
            pygame.draw.rect(self.tela, CORES[cor], preenchido, border_radius=self.medida(8))

    def mascote(self, expressao, area):
        self.ilustracao(f"mascote_{expressao}.svg", area)

    def acao_clicada(self, posicao):
        for area, acao in self.botoes:
            if area.collidepoint(posicao):
                return acao
        return None

    def mover_foco(self, direcao):
        if self.botoes:
            if self.foco_ativo:
                self.foco = (self.foco + direcao) % len(self.botoes)
            else:
                self.foco = 0 if direcao > 0 else len(self.botoes) - 1
            self.foco_ativo = True

    def acao_focada(self):
        if self.botoes:
            return self.botoes[self.foco % len(self.botoes)][1]
        return None
