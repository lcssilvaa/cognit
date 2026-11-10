"""Regras das salas, sem HTTP e sem Pygame.

O servidor decide prazos, dicas, respostas e pontos. O cliente recebe apenas
os dados permitidos para sua sessão; o gabarito só é publicado no placar.
"""

from dataclasses import dataclass, field
import secrets
from threading import RLock
from time import monotonic

from config import EXPIRACAO_SALA, MAX_JOGADORES, TEMPO_DESCONEXAO
from avatares import AVATARES, AVATAR_PADRAO
from temas import TEMAS, catalogo_temas
from tempo import espera_da_dica, limite_da_pergunta


class ErroSala(ValueError):
    """Erro esperado, cuja mensagem pode ser apresentada ao jogador."""


@dataclass
class Jogador:
    nome: str
    icone: str = AVATAR_PADRAO
    visto_em: float = 0.0
    id: str = field(default_factory=lambda: secrets.token_hex(6))
    pontos: int = 0
    acertos: int = 0
    resposta: int | None = None
    usou_dica: bool = False
    ganho: int = 0
    sequencia: int = 0
    posicao_anterior: int = 1
    pronto: bool = False


@dataclass
class Sala:
    codigo: str
    tema: str
    anfitriao: str
    jogadores: dict[str, Jogador]  # A chave é o token privado da sessão.
    atividade: float
    fase: str = "espera"
    indice: int = 0
    inicio: float = 0.0

    @property
    def perguntas(self):
        return TEMAS[self.tema]["perguntas"]

    @property
    def pergunta(self):
        return self.perguntas[self.indice]


class GerenciadorSalas:
    """Uma instância por servidor. O lock serializa requisições concorrentes."""

    def __init__(self, relogio=monotonic):
        self.salas: dict[str, Sala] = {}
        self.relogio = relogio
        self.lock = RLock()

    def executar(self, acao, dados):
        with self.lock:
            agora = self.relogio()
            self.salas = {c: s for c, s in self.salas.items()
                          if agora - s.atividade < EXPIRACAO_SALA}
            if acao == "catalogo":
                return {"temas": catalogo_temas()}
            if acao == "criar":
                return self._criar(dados, agora)
            sala = self.salas.get(str(dados.get("codigo", "")).strip())
            if sala is None:
                raise ErroSala("Sala não encontrada ou encerrada. Confira o código.")
            if acao == "entrar":
                return self._entrar(sala, dados, agora)
            token = dados.get("token")
            if not isinstance(token, str) or token not in sala.jogadores:
                raise ErroSala("Sua sessão não pertence a esta sala.")
            jogador = sala.jogadores[token]
            jogador.visto_em = agora
            sala.atividade = agora
            # Uma aba fechada não pode deixar todos presos aguardando o host.
            host = sala.jogadores[sala.anfitriao]
            if agora - host.visto_em >= TEMPO_DESCONEXAO:
                sala.anfitriao = token
            self._atualizar(sala, agora)
            if acao == "sair":
                self._sair(sala, token, agora)
                return {"saiu": True}
            if acao in ("iniciar", "proxima"):
                self._avancar(sala, token, acao, agora)
            elif acao == "pronto":
                if sala.fase != "espera":
                    raise ErroSala("A partida já começou.")
                jogador.pronto = not jogador.pronto
            elif acao == "responder":
                self._responder(sala, jogador, dados, agora)
            elif acao == "dica":
                self._pedir_dica(sala, jogador, dados, agora)
            elif acao != "estado":
                raise ErroSala("Ação desconhecida.")
            return self._estado(sala, token, agora)

    def _sair(self, sala, token, agora):
        del sala.jogadores[token]
        if not sala.jogadores:
            del self.salas[sala.codigo]
            return
        if sala.anfitriao == token:
            sala.anfitriao = next(iter(sala.jogadores))
        self._atualizar(sala, agora)

    def _avancar(self, sala, token, acao, agora):
        if token != sala.anfitriao:
            raise ErroSala("Somente o anfitrião pode iniciar ou avançar.")
        if acao == "iniciar":
            if sala.fase != "espera" or len(sala.jogadores) < 2:
                raise ErroSala("Aguarde pelo menos dois jogadores para iniciar.")
            self._iniciar_pergunta(sala, agora)
        elif sala.fase != "placar":
            raise ErroSala("Aguarde o encerramento da pergunta.")
        elif sala.indice + 1 == len(sala.perguntas):
            sala.fase = "final"
        else:
            sala.indice += 1
            self._iniciar_pergunta(sala, agora)

    @staticmethod
    def _validar_pergunta(sala, jogador, dados):
        indice = dados.get("indice")
        if sala.fase != "pergunta" or type(indice) is not int or indice != sala.indice:
            raise ErroSala("Esta pergunta já encerrou. Aguarde o placar.")
        if jogador.resposta is not None:
            raise ErroSala("Sua resposta já foi registrada.")

    def _pedir_dica(self, sala, jogador, dados, agora):
        self._validar_pergunta(sala, jogador, dados)
        espera = espera_da_dica(limite_da_pergunta(sala.indice))
        if agora - sala.inicio < espera:
            raise ErroSala("A dica ainda não foi liberada.")
        jogador.usou_dica = True

    def _responder(self, sala, jogador, dados, agora):
        self._validar_pergunta(sala, jogador, dados)
        alternativa = dados.get("alternativa")
        if type(alternativa) is not int or not 0 <= alternativa < len(sala.pergunta["alternativas"]):
            raise ErroSala("Alternativa inválida.")
        jogador.resposta = alternativa
        if alternativa == sala.pergunta["correta"]:
            limite = limite_da_pergunta(sala.indice)
            restante = max(0, limite - (agora - sala.inicio))
            jogador.ganho = round(500 + 500 * restante / limite)
            if jogador.usou_dica:
                jogador.ganho -= 200
        self._atualizar(sala, agora)

    @staticmethod
    def _nome(dados):
        nome = dados.get("nome", "")
        if not isinstance(nome, str):
            raise ErroSala("Informe seu apelido.")
        nome = " ".join(nome.split())
        if not 1 <= len(nome) <= 20 or not nome.isprintable():
            raise ErroSala("Use um apelido de 1 a 20 caracteres.")
        return nome

    def _criar(self, dados, agora):
        tema = dados.get("tema", "tecnologia")
        if not isinstance(tema, str) or tema not in TEMAS or not TEMAS[tema].get("perguntas"):
            raise ErroSala("Escolha um tema disponível.")
        nome = self._nome(dados)
        icone = self._icone(dados)
        if len(self.salas) >= 500:
            raise ErroSala("Servidor cheio. Tente novamente mais tarde.")
        codigo = str(secrets.randbelow(900000) + 100000)
        while codigo in self.salas:
            codigo = str(secrets.randbelow(900000) + 100000)
        token = secrets.token_urlsafe(24)
        sala = Sala(codigo, tema, token, {token: Jogador(nome, icone=icone, visto_em=agora, pronto=True)}, agora)
        self.salas[codigo] = sala
        return {**self._estado(sala, token, agora), "token": token}

    def _entrar(self, sala, dados, agora):
        if sala.fase != "espera":
            raise ErroSala("Esta partida já começou. Crie outra sala para jogar.")
        if len(sala.jogadores) >= MAX_JOGADORES:
            raise ErroSala("Esta sala está cheia.")
        nome = self._nome(dados)
        icone = self._icone(dados)
        if any(j.nome.casefold() == nome.casefold() for j in sala.jogadores.values()):
            raise ErroSala("Este apelido já está em uso na sala.")
        token = secrets.token_urlsafe(24)
        sala.jogadores[token] = Jogador(nome, icone=icone, visto_em=agora)
        sala.atividade = agora
        return {**self._estado(sala, token, agora), "token": token}

    def _iniciar_pergunta(self, sala, agora):
        sala.fase = "pergunta"
        sala.inicio = agora
        for jogador in sala.jogadores.values():
            jogador.posicao_anterior = self._posicao(sala, jogador)
            jogador.resposta = None
            jogador.usou_dica = False
            jogador.ganho = 0

    def _atualizar(self, sala, agora):
        if sala.fase == "pergunta":
            acabou = agora - sala.inicio >= limite_da_pergunta(sala.indice)
            todos = all(j.resposta is not None for j in sala.jogadores.values())
            if acabou or todos:
                # Somente aqui os totais mudam. Antes do fechamento nem pontos,
                # acertos nem a ordem da lista permitem deduzir o resultado.
                for jogador in sala.jogadores.values():
                    acertou = jogador.resposta == sala.pergunta["correta"]
                    jogador.pontos += jogador.ganho
                    jogador.acertos += int(acertou)
                    jogador.sequencia = jogador.sequencia + 1 if acertou else 0
                sala.fase = "placar"

    @staticmethod
    def _icone(dados):
        icone = dados.get("icone", AVATAR_PADRAO)
        if not isinstance(icone, str) or icone not in AVATARES:
            raise ErroSala("Escolha um dos ícones disponíveis.")
        return icone

    @staticmethod
    def _posicao(sala, jogador):
        """Empates de pontos e acertos compartilham a mesma posição."""
        return 1 + sum((j.pontos, j.acertos) > (jogador.pontos, jogador.acertos)
                       for j in sala.jogadores.values())

    def _estado(self, sala, token, agora):
        jogador = sala.jogadores[token]
        limite = limite_da_pergunta(sala.indice)
        decorrido = max(0, agora - sala.inicio) if sala.fase != "espera" else 0
        ranking = sorted(sala.jogadores.values(), key=lambda j: (-j.pontos, -j.acertos, j.nome.casefold()))
        estado = {
            "codigo": sala.codigo, "tema": sala.tema,
            "nome_tema": TEMAS[sala.tema]["nome"], "fase": sala.fase,
            "anfitriao": token == sala.anfitriao, "indice": sala.indice,
            "total": len(sala.perguntas), "limite": limite,
            "restante": max(0, limite - decorrido) if sala.fase == "pergunta" else 0,
            "espera_dica": max(0, espera_da_dica(limite) - decorrido),
            "respondidos": sum(j.resposta is not None for j in sala.jogadores.values()),
            "jogadores": [{"id": j.id, "nome": j.nome, "icone": j.icone, "pontos": j.pontos,
                           "acertos": j.acertos, "pronto": j.pronto,
                           "online": agora - j.visto_em < TEMPO_DESCONEXAO,
                           "posicao": self._posicao(sala, j),
                           "anfitriao": j is sala.jogadores[sala.anfitriao]}
                          for j in ranking],
            "voce": {"id": jogador.id, "respondeu": jogador.resposta is not None,
                     "icone": jogador.icone,
                     "pronto": jogador.pronto,
                     "alternativa": jogador.resposta, "pontos": jogador.pontos,
                     "usou_dica": jogador.usou_dica},
        }
        if sala.fase != "espera":
            estado["pergunta"] = {k: sala.pergunta[k] for k in
                                  ("enunciado", "alternativas", "dificuldade", "codigo")
                                  if k in sala.pergunta}
            if jogador.usou_dica:
                estado["dica"] = sala.pergunta.get("dica", "Leia o enunciado com atenção.")
        if sala.fase in ("placar", "final"):
            estado["correta"] = sala.pergunta["correta"]
            estado["explicacao"] = sala.pergunta["explicacao"]
            resultado = "sem_resposta" if jogador.resposta is None else (
                "acertou" if jogador.resposta == sala.pergunta["correta"] else "errou")
            posicao = self._posicao(sala, jogador)
            estado["voce"].update(
                ganho=jogador.ganho, resultado=resultado, posicao=posicao,
                movimento=jogador.posicao_anterior - posicao,
                sequencia=jogador.sequencia, acertos=jogador.acertos,
            )
        return estado
