"""Regras do quiz, independentes da janela e dos desenhos do Pygame."""

from config import VIDAS_INICIAIS
from perguntas import PERGUNTAS
from tempo import espera_da_dica, limite_da_pergunta


class Partida:
    def __init__(self, perguntas=None, vidas=VIDAS_INICIAIS):
        self.perguntas = PERGUNTAS if perguntas is None else perguntas
        if not self.perguntas or vidas < 1:
            raise ValueError("A partida precisa de perguntas e pelo menos uma vida.")
        for pergunta in self.perguntas:
            alternativas = pergunta["alternativas"]
            if not 2 <= len(alternativas) <= 4:
                raise ValueError("Cada pergunta precisa de 2 a 4 alternativas.")
            if not 0 <= pergunta["correta"] < len(alternativas):
                raise ValueError("A resposta correta deve apontar para uma alternativa.")

        self.vidas_iniciais = vidas
        self.vidas = vidas
        self.indice = 0
        self.acertos = 0
        self.erros = 0
        self.ultimo_acerto = None
        self.alternativas_erradas = set()
        self.tempo_decorrido = 0.0
        self.tempo_esgotado = False
        self.dica_visivel = False

    @property
    def tempo_limite(self):
        return limite_da_pergunta(self.indice)

    @property
    def tempo_restante(self):
        return max(0.0, self.tempo_limite - self.tempo_decorrido)

    @property
    def espera_dica(self):
        return max(0.0, espera_da_dica(self.tempo_limite) - self.tempo_decorrido)

    def revelar_dica(self):
        if self.ultimo_acerto is None and self.espera_dica == 0 and self.pergunta.get("dica"):
            self.dica_visivel = True
        return self.dica_visivel

    def atualizar_tempo(self, segundos):
        """Chamado apenas na pergunta: feedback e confirmação de saída pausam."""
        if self.ultimo_acerto is not None or self.venceu or self.perdeu:
            return
        self.tempo_decorrido += max(0, segundos)
        if self.tempo_restante == 0:
            self.tempo_esgotado = True
            self.ultimo_acerto = False
            self.vidas -= 1
            self.erros += 1

    @property
    def pergunta(self):
        return self.perguntas[self.indice]

    @property
    def progresso(self):
        return round(self.acertos / len(self.perguntas) * 100)

    @property
    def venceu(self):
        return self.acertos == len(self.perguntas)

    @property
    def perdeu(self):
        return self.vidas == 0

    def responder(self, alternativa):
        """Retorna True/False para acerto/erro, ou None se a ação for ignorada."""
        if self.venceu or self.perdeu or self.ultimo_acerto is not None:
            return None
        if alternativa in self.alternativas_erradas:
            return None
        if not 0 <= alternativa < len(self.pergunta["alternativas"]):
            return None

        self.ultimo_acerto = alternativa == self.pergunta["correta"]
        if self.ultimo_acerto:
            self.acertos += 1
        else:
            self.vidas -= 1
            self.erros += 1
            self.alternativas_erradas.add(alternativa)
        return self.ultimo_acerto

    def continuar(self):
        """Só um acerto libera a próxima pergunta. Um erro permite tentar de novo."""
        if self.ultimo_acerto is None:
            return
        if self.ultimo_acerto and not self.venceu:
            self.indice += 1
            self.alternativas_erradas.clear()
        # Errar uma alternativa mantém o tempo restante. Um timeout concede
        # uma nova tentativa com o mesmo limite, descontando uma única vida.
        if self.ultimo_acerto or self.tempo_esgotado:
            self.tempo_decorrido = 0.0
            self.dica_visivel = False
        self.tempo_esgotado = False
        self.ultimo_acerto = None
