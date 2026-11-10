"""Cartões de tema compartilhados pelo solo e pelo formulário de salas.

O catálogo único em temas.py define as opções dos dois modos. Esta tabela
apenas associa o identificador de cada tema à sua ilustração.
"""

TEMAS_POR_PAGINA = 2
ICONES_TEMA = {
    "tecnologia": "tema_tecnologia.svg",
    "ux_design": "tema_ux_design.svg",
}


def desenhar_opcao_tema(ui, tema, area, acao, selecionado=False):
    """Opção de sala com descrição, quantidade de perguntas e estado explícito."""
    x, y, largura, altura = area
    arquivo = ICONES_TEMA.get(tema.get("icone", tema["id"]), ICONES_TEMA["tecnologia"])
    ui.cartao(area, "branco", "azul" if selecionado else "borda", 24)
    ui.cartao((x + 18, y + 18, 84, 84), "azul_claro", None, 22)
    ui.ilustracao(arquivo, (x + 24, y + 24, 72, 72))
    ui.rotulo(tema["nome"], (x + 118, y + 23, largura - 142, 36), 24, "azul_escuro", True)
    ui.cartao((x + 118, y + 68, 132, 28), "azul_claro", None, 14)
    ui.paragrafo(f"{tema['total']} perguntas", (x + 122, y + 68, 124, 28),
                 14, "azul", True, True)
    ui.paragrafo(tema.get("descricao", "Um novo assunto para desafiar sua mente."),
                 (x + 22, y + 112, largura - 44, 46), 17, "secundario")
    if selecionado:
        ui.cartao((x + 18, y + altura - 42, largura - 36, 30), "verde_claro", None, 15)
        ui.simbolo_resultado(True, (x + 36, y + altura - 27), 7, "verde")
        ui.rotulo("Tema selecionado", (x + 54, y + altura - 42, largura - 86, 30),
                  15, "verde", True)
    else:
        ui.rotulo("Escolher este tema  >", (x + 22, y + altura - 43, largura - 44, 32),
                  16, "azul", True)
    ui.area_interativa(area, acao)


def desenhar_cartao_tema(ui, tema, area, acao=None, compacto=False, *,
                        selecionado=False, rotulo_acao="Jogar agora"):
    x, y, largura, altura = area
    arquivo = ICONES_TEMA.get(tema.get("icone", tema["id"]), ICONES_TEMA["tecnologia"])
    ui.cartao(area, "branco", "azul" if selecionado else None, 24)
    if compacto:
        ui.ilustracao(arquivo, (x + 14, y + 15, 66, 66))
        ui.rotulo(tema["nome"], (x + 98, y + 18, largura - 132, 32), 22, "azul_escuro", True)
        ui.texto(f"{tema['total']} perguntas", (x + 98, y + 59), 14, "secundario")
        if acao:
            ui.texto(">", (x + largura - 29, y + 35), 22, "azul", True)
    else:
        ui.ilustracao(arquivo, (x + 18, y + 23, 80, 80))
        ui.rotulo(tema["nome"], (x + 116, y + 20, largura - 134, 36), 25, "azul_escuro", True)
        ui.paragrafo(tema.get("descricao", "Um novo assunto para desafiar sua mente."),
                     (x + 116, y + 62, largura - 136, 53), 15, "secundario")
        ui.texto(f"{tema['total']} perguntas", (x + 22, y + altura - 48), 15, "secundario")
        ui.cartao((x + largura - 164, y + altura - 65, 142, 44), "azul", None, 22)
        ui.paragrafo(rotulo_acao, (x + largura - 158, y + altura - 62, 130, 38),
                     17, "branco", True, True)
    if acao:
        # Um único alvo por cartão, inclusive por teclado: todo o cartão responde.
        ui.area_interativa(area, acao)
