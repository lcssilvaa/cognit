"""Controlador das salas: ações, perfil e sincronização assíncrona.

Desenhos e animações: visuais_sala.py. Regras: salas.py.
O endereço da conexão é configuração da aplicação, sem campo no menu.
"""

import asyncio
import json
import platform
import sys
from time import monotonic

import pygame

from avatares import AVATARES, AVATAR_PADRAO
from config import INTERVALO_SINCRONIZACAO, SERVIDOR_PADRAO
from rede import ClienteSalas, ErroRede
from visuais_sala import VisuaisSala
from visuais_temas import TEMAS_POR_PAGINA


class TelasSala:
    def __init__(self, jogo):
        self.jogo = jogo
        self.endereco = str(platform.window.cognit_servidor) if sys.platform == "emscripten" else SERVIDOR_PADRAO
        self.campos = {"nome": "", "codigo": ""}
        self.campo_ativo = None
        self.icone = AVATAR_PADRAO
        self.temas = []
        self.tema = None
        self.modo = "criar"
        self.escolhendo_icone = False
        self.escolhendo_tema = False
        self.pagina_temas = 0
        self.cliente = None
        self.estado = None
        self.token = None
        self.tarefa = None
        self.acao_pendente = None
        self.comando_aguardando = None
        self.proxima_consulta = 0.0
        self.recebido_em = 0.0
        self.fase_em = monotonic()
        self.painel_rodada = "feedback"
        self.detalhe_podio = None
        self.explicacao_visivel = False
        self.erro = self.erro_conexao = ""
        self.confirmando_saida = self.saindo = False
        self.visuais = VisuaisSala(self)

    def _enviar(self, acao, **dados):
        if self.tarefa is not None:
            if self.acao_pendente == "estado" and acao != "estado" and self.comando_aguardando is None:
                self.comando_aguardando = (acao, dados)
            return
        if self.token:
            dados.update(codigo=self.estado["codigo"], token=self.token)
        self.acao_pendente = acao
        self.tarefa = asyncio.create_task(self.cliente.requisitar(acao, dados))

    def _carregar_catalogo(self):
        if self.tarefa is not None:
            return
        self.erro = ""
        try:
            self.cliente = ClienteSalas(self.endereco)
        except ErroRede:
            self.erro = "Não foi possível conectar. Tente novamente em instantes."
            return
        self._enviar("catalogo")

    @property
    def ocupado(self):
        return self.comando_aguardando is not None or (
            self.tarefa is not None and self.acao_pendente != "estado")

    def atualizar(self):
        """Aplica respostas de rede sem reiniciar animações a cada consulta."""
        agora = monotonic()
        if self.tarefa is not None and self.tarefa.done():
            acao = self.acao_pendente
            try:
                resposta = self.tarefa.result()
            except ErroRede as erro:
                if acao == "estado":
                    self.erro_conexao = "Reconectando à sala…"
                elif acao == "catalogo":
                    self.erro = "Não foi possível conectar. Tente novamente em instantes."
                else:
                    self.erro = str(erro)
            else:
                self.erro_conexao = ""
                if acao == "catalogo":
                    self._aplicar_catalogo(resposta["temas"])
                elif acao != "sair":
                    self._aplicar_estado(resposta, agora)
                    if acao in ("criar", "entrar"):
                        self.jogo.navegar("sala")
                    if acao != "estado":
                        self.erro = ""
            self.tarefa = None
            self.acao_pendente = None
            self.proxima_consulta = agora + (2 if self.erro_conexao else INTERVALO_SINCRONIZACAO)
            if acao == "sair":
                self._limpar()
                self.jogo.navegar("amigos")
        if self.saindo and self.tarefa is None and self.token:
            self.comando_aguardando = None
            self._enviar("sair")
        elif self.comando_aguardando is not None and self.tarefa is None:
            acao, dados = self.comando_aguardando
            self.comando_aguardando = None
            self._enviar(acao, **dados)
        elif self.token and self.tarefa is None and agora >= self.proxima_consulta:
            self._enviar("estado")

    def _aplicar_catalogo(self, temas):
        self.temas = temas
        if self.tema not in [tema["id"] for tema in temas]:
            self.tema = temas[0]["id"] if temas else None
        ultima_pagina = max(0, (len(temas) - 1) // TEMAS_POR_PAGINA)
        self.pagina_temas = min(self.pagina_temas, ultima_pagina)
        if not temas:
            self.erro = "Ainda não há temas disponíveis para jogar."

    def _aplicar_estado(self, estado, agora):
        """Só a mudança de rodada/fase reinicia o feedback; o polling não reinicia."""
        fase_anterior = (self.estado["indice"], self.estado["fase"]) if self.estado else None
        fase_atual = (estado["indice"], estado["fase"])
        if fase_anterior != fase_atual:
            self.fase_em = agora
            self.painel_rodada = "feedback"
            self.detalhe_podio = None
            self.explicacao_visivel = False
            self.erro = ""
            self.jogo.ui.foco_ativo = False
        self.token = estado.get("token", self.token)
        self.estado = estado
        self.recebido_em = agora

    def _limpar(self):
        self.token = self.estado = None
        self.erro = self.erro_conexao = ""
        self.confirmando_saida = self.saindo = False
        self.comando_aguardando = None

    def executar_acao(self, acao):
        acoes_de_menu = (
            "sala_modo_criar", "sala_modo_entrar", "sala_escolher_icone", "sala_usar_icone",
            "sala_escolher_tema", "sala_voltar_temas", "sala_temas_anterior", "sala_temas_proxima",
        )
        if acao in acoes_de_menu or acao.startswith("sala_tema_"):
            self.jogo.ui.botoes = []
            self.jogo.ui.foco = 0
            self.jogo.ui.foco_ativo = False
        if acao == "amigos":
            self.erro = ""
            self.escolhendo_icone = False
            self.escolhendo_tema = False
            self.jogo.navegar("amigos")
            self._carregar_catalogo()
        elif acao == "sala_reconectar":
            self._carregar_catalogo()
        elif acao.startswith("campo_"):
            self._editar_campo(acao.removeprefix("campo_"))
        elif acao in ("sala_modo_criar", "sala_modo_entrar"):
            self.modo = acao.removeprefix("sala_modo_")
            self.campo_ativo = None
            self.erro = ""
            pygame.key.stop_text_input()
        elif acao == "sala_escolher_icone":
            self.campo_ativo = None
            pygame.key.stop_text_input()
            self.escolhendo_icone = True
        elif acao.startswith("sala_icone_"):
            icone = acao.removeprefix("sala_icone_")
            if icone in AVATARES:
                self.icone = icone
        elif acao == "sala_usar_icone":
            self.escolhendo_icone = False
        elif acao == "sala_escolher_tema" and self.temas:
            self.campo_ativo = None
            pygame.key.stop_text_input()
            self.escolhendo_tema = True
            ids = [tema["id"] for tema in self.temas]
            self.pagina_temas = ids.index(self.tema) // TEMAS_POR_PAGINA if self.tema in ids else 0
        elif acao == "sala_voltar_temas":
            self.escolhendo_tema = False
        elif acao in ("sala_temas_anterior", "sala_temas_proxima"):
            direcao = 1 if acao == "sala_temas_proxima" else -1
            ultima_pagina = max(0, (len(self.temas) - 1) // TEMAS_POR_PAGINA)
            self.pagina_temas = max(0, min(self.pagina_temas + direcao, ultima_pagina))
        elif acao.startswith("sala_tema_"):
            tema = acao.removeprefix("sala_tema_")
            if tema in [t["id"] for t in self.temas]:
                self.tema = tema
                self.escolhendo_tema = False
        elif acao in ("sala_criar", "sala_entrar"):
            self._participar(acao)
        elif acao == "sala_sair":
            self.confirmando_saida = True
        elif acao == "sala_ficar":
            self.confirmando_saida = False
        elif acao == "sala_confirmar_saida":
            self.saindo = True
        elif self.estado and not self.confirmando_saida:
            if acao in ("sala_iniciar", "sala_proxima", "sala_pronto"):
                self._enviar(acao.removeprefix("sala_"))
            elif acao.startswith("resposta_") and not self.estado["voce"]["respondeu"]:
                self._enviar("responder", indice=self.estado["indice"],
                             alternativa=int(acao.rsplit("_", 1)[1]))
            elif acao == "dica":
                self._enviar("dica", indice=self.estado["indice"])
            elif acao == "sala_ver_placar":
                self.painel_rodada = "ranking"
                self.explicacao_visivel = False
            elif acao == "sala_ver_explicacao":
                self.explicacao_visivel = True
            elif acao == "sala_ver_resposta":
                self.painel_rodada = "feedback"
                self.fase_em = monotonic()
            elif acao == "sala_rever_podio":
                self.fase_em = monotonic()
            elif acao.startswith("sala_podio_"):
                self.detalhe_podio = acao.removeprefix("sala_podio_")

    def _participar(self, acao):
        if self.tarefa is not None:
            return
        self.campo_ativo = None
        pygame.key.stop_text_input()
        if not self.campos["nome"].strip():
            self.erro = "Escolha seu nome para continuar."
            return
        if acao == "sala_entrar" and len(self.campos["codigo"]) != 6:
            self.erro = "Digite o código de 6 números da sala."
            return
        if acao == "sala_criar" and self.tema is None:
            self.erro = "Aguarde o carregamento dos temas."
            return
        if self.cliente is None:
            self._carregar_catalogo()
            return
        self.erro = ""
        perfil = {"nome": self.campos["nome"], "icone": self.icone}
        if acao == "sala_criar":
            self._enviar("criar", **perfil, tema=self.tema)
        else:
            self._enviar("entrar", **perfil, codigo=self.campos["codigo"])

    def _editar_campo(self, campo):
        if campo not in self.campos:
            return
        if sys.platform == "emscripten":
            valor = json.loads(str(platform.window.cognit_pedir_texto(campo, self.campos[campo])))
            if valor is not None:
                self.campos[campo] = self._filtrar(campo, str(valor))
        else:
            self.campo_ativo = campo
            pygame.key.start_text_input()

    @staticmethod
    def _filtrar(campo, valor):
        if campo == "codigo":
            return "".join(c for c in valor if c in "0123456789")[:6]
        return "".join(c for c in valor if c.isprintable())[:20]

    def tratar_texto(self, evento):
        if not self.campo_ativo:
            return False
        campo = self.campo_ativo
        if evento.type == pygame.TEXTINPUT:
            self.campos[campo] = self._filtrar(campo, self.campos[campo] + evento.text)
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_BACKSPACE:
                self.campos[campo] = self.campos[campo][:-1]
            elif evento.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_TAB):
                self.campo_ativo = None
                pygame.key.stop_text_input()
            elif evento.key == pygame.K_v and evento.mod & pygame.KMOD_CTRL:
                try:
                    texto = pygame.scrap.get_text()
                except pygame.error:
                    texto = ""
                self.campos[campo] = self._filtrar(campo, self.campos[campo] + texto)
            elif evento.key == pygame.K_a and evento.mod & pygame.KMOD_CTRL:
                self.campos[campo] = ""
        return evento.type in (pygame.TEXTINPUT, pygame.KEYDOWN, pygame.KEYUP)

    def desenhar(self):
        self.visuais.desenhar()

    async def fechar(self):
        if self.tarefa is not None:
            self.tarefa.cancel()
            await asyncio.gather(self.tarefa, return_exceptions=True)
        if self.token:
            try:
                await self.cliente.requisitar("sair", {"codigo": self.estado["codigo"], "token": self.token})
            except ErroRede:
                pass
