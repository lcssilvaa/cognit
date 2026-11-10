"""Cartões de tema compartilhados pelo solo e pelo formulário de salas.

O catálogo único em temas.py define as opções dos dois modos. Esta tabela
apenas associa o identificador de cada tema à sua ilustração.
"""

TEMAS_POR_PAGINA = 2
ICONES_TEMA = {
    "tecnologia": "tema_tecnologia.svg",
    "ux_design": "tema_ux_design.svg",
}


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
