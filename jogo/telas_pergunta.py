"""Layout de perguntas dos dois modos: uma hierarquia simples, sem cartões aninhados."""

from math import ceil


def desenhar_cabecalho(ui, indice, total, tema, restante, limite, sair):
    ui.icone_fechar((24, 42, 44, 44), sair)
    ui.texto(f"{indice + 1} de {total}", (92, 54), 17, "secundario")
    desenhar_relogio(ui, restante, limite)
    ui.rotulo(tema, (24, 109, 244, 26), 14, "secundario")


def desenhar_relogio(ui, restante, limite):
    cor = "vermelho" if restante <= min(5, limite / 4) else "azul_escuro"
    ui.cartao((278, 42, 88, 44), "branco", None, 14)
    ui.texto(f"{ceil(max(0, restante))} s", (322, 51), 22, cor, True, True)


def desenhar_enunciado(ui, pergunta):
    # O enunciado fica direto no fundo. Só o trecho de código recebe um bloco.
    if pergunta.get("codigo"):
        ui.paragrafo(pergunta["enunciado"], (24, 151, 342, 100), 27, negrito=True)
        ui.cartao((24, 273, 342, 112), "azul_escuro", None, 18)
        ui.paragrafo(pergunta["codigo"], (44, 287, 302, 84), 18, "branco")
    else:
        ui.paragrafo(pergunta["enunciado"], (24, 153, 342, 218), 29, negrito=True)


def desenhar_alternativas(ui, pergunta, desativadas=(), bloqueadas=False):
    for i, alternativa in enumerate(pergunta["alternativas"]):
        ui.alternativa(i, alternativa, (24, 424 + i * 78, 342, 66),
                       bloqueadas or i in desativadas)


def desenhar_dica(ui, espera, dica=None, habilitada=True, tem_dica=True):
    if not tem_dica:
        return
    disponivel = habilitada and espera <= 0
    ui.mascote("feliz" if disponivel else "pensativo", (24, 766, 46, 40))
    if dica:
        ui.paragrafo(dica, (86, 748, 280, 76), 16, "secundario")
    else:
        aviso = f"Dica em {ceil(espera)} s" if espera > 0 else "Pedir dica"
        ui.texto(aviso, (86, 778), 16, "azul" if disponivel else "secundario")
    ui.area_interativa((24, 746, 342, 80), "dica", disponivel and not dica)
