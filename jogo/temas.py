"""Catálogo único de temas para jogar sozinho e com amigos.

Para adicionar: importe uma nova lista de perguntas e acrescente uma entrada
com nome e perguntas a TEMAS. Reinicie o servidor após editar o cadastro.
"""

from perguntas import PERGUNTAS
from perguntas_ux_design import PERGUNTAS_UX_DESIGN


TEMAS = {
    "tecnologia": {
        "nome": "Tecnologia",
        "descricao": "Programação, internet e novas descobertas.",
        "icone": "tecnologia",
        "perguntas": PERGUNTAS,
    },
    "ux_design": {
        "nome": "UX e Design",
        "descricao": "Usabilidade, protótipos e Figma na prática.",
        "icone": "ux_design",
        "perguntas": PERGUNTAS_UX_DESIGN,
    },
}


def catalogo_temas():
    """Um cadastro sem perguntas não deve aparecer como opção jogável."""
    return [{"id": id_tema, "nome": tema["nome"], "total": len(tema["perguntas"]),
             "descricao": tema.get("descricao", "Um novo assunto para desafiar sua mente."),
             "icone": tema.get("icone", id_tema)}
            for id_tema, tema in TEMAS.items() if tema.get("perguntas")]
