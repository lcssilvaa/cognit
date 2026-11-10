"""Recria as variantes SVG do mascote: python scripts/gerar_avatares.py.

As formas permanecem vetoriais e editáveis. Não altera o mascote original.
"""

from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET

ASSETS = Path(__file__).resolve().parents[1] / "jogo" / "assets"
SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)


def estrela(x, y, tamanho=5):
    return f'<path transform="translate({x} {y}) scale({tamanho / 10})" d="M0-10 3-3 10-3 5 2 6 10 0 6-6 10-5 2-10-3-3-3Z" fill="white"/>'


VARIANTES = {
    "classico": ("#EAF2FB", "", ""),
    "vice_city": ("#F6D9F7", '''
        <path d="M174 134Q184 82 192 36" fill="none" stroke="#139D9C" stroke-width="8"/>
        <path d="M192 36Q169 12 150 38Q171 29 192 36Q205 9 219 27Q207 27 192 36Q218 29 228 50Q207 40 192 36" fill="#25B9B0"/>
        ''', '''
        <rect x="49" y="73" width="44" height="30" rx="10" fill="#372C64" stroke="#28D8D0" stroke-width="3"/>
        <rect x="107" y="73" width="44" height="30" rx="10" fill="#372C64" stroke="#F260BD" stroke-width="3"/>
        <path d="M93 81H107M53 77 45 73M147 77 156 73" stroke="#372C64" stroke-width="5"/>
        <path d="M57 78 76 95M115 78 134 95" stroke="white" stroke-opacity=".4" stroke-width="3"/>
        <path d="M50 142 75 134 100 146 125 134 150 142 152 160H48Z" fill="#18B7B0"/>
        <path d="M75 135 100 157 125 135" fill="none" stroke="#FFF5BA" stroke-width="5"/>
        '''),
    "hyrule": ("#DFF4DF", '''
        <path d="M49 156 178 30" stroke="#9DBFCB" stroke-width="9"/>
        <path d="M149 32 180 61" stroke="#C3A64D" stroke-width="10" stroke-linecap="round"/>
        ''', '''
        <path d="M39 43Q75-11 120 0L182 47Q147 33 133 55Z" fill="#33945C"/>
        <path d="M43 43Q91 24 139 48L133 59Q88 41 40 55Z" fill="#74BD63"/>
        <path d="M24 87 8 64 39 74M177 87 193 64 162 74" fill="#FFD3AB" stroke="#E0A36C" stroke-width="3"/>
        <path d="M100 126 111 146H89ZM88 147 99 166H77ZM112 147 123 166H101Z" fill="#F1BB35"/>
        '''),
    "cruzeiro": ("#DCEAFF", "", '''
        <path d="M38 140 64 130 100 143 136 130 162 140 154 164H46Z" fill="#154696"/>
        <path d="M79 135Q100 155 121 135" fill="none" stroke="white" stroke-width="5"/>
        ''' + ''.join(estrela(x, y, r) for x, y, r in [(100, 23, 6), (81, 40, 5), (119, 40, 5), (100, 57, 6), (115, 61, 3)])),
    "ninja": ("#FFF0D4", '''
        <path d="M46 65 11 116 44 105 25 143 64 100" fill="#293E61"/>
        ''', '''
        <path d="M36 44Q100 26 164 44L161 68Q100 52 39 68Z" fill="#253E60"/>
        <rect x="72" y="37" width="57" height="29" rx="7" fill="#D3DFE5" stroke="#8A9EAE" stroke-width="3"/>
        <path d="M111 45Q89 39 91 53Q94 64 107 56Q113 48 102 47Q95 47 98 54M91 52 84 58" fill="none" stroke="#455E70" stroke-width="3" stroke-linecap="round"/>
        <path d="M43 108 60 112M41 120 58 120M140 112 157 108M142 120H159" stroke="#75475B" stroke-width="3"/>
        <path d="M49 142 75 133 100 145 125 133 151 142 153 163H47Z" fill="#EF8D2F"/>
        <path d="M99 144V163" stroke="#293E61" stroke-width="5"/>
        '''),
    "mago": ("#EEE5F6", "", '''
        <path d="M72 22Q86 6 100 18L125 1 116 30 103 23 94 40 91 24Z" fill="#573B38"/>
        <path d="M111 31 102 44 114 45 103 60" fill="none" stroke="#E9A82E" stroke-width="4"/>
        <path d="M62 138Q100 154 138 138L133 162H67Z" fill="#9B344C"/>
        <path d="M78 145V163M104 149V163M127 144V162" stroke="#EABB4D" stroke-width="9"/>
        <path d="M161 151 183 103" stroke="#765333" stroke-width="6" stroke-linecap="round"/>
        <path d="M183 92V110M174 101H192M177 95 189 107M177 107 189 95" stroke="#E6B547" stroke-width="3"/>
        '''),
}


def gerar():
    original = ET.parse(ASSETS / "mascote_feliz.svg").getroot()[0]
    for id_icone, (fundo, atras, frente) in VARIANTES.items():
        raiz = ET.Element(f"{{{SVG}}}svg", width="240", height="240", viewBox="0 0 240 240")
        raiz.append(ET.fromstring(f'<circle xmlns="{SVG}" cx="120" cy="120" r="116" fill="{fundo}"/>'))
        grupo = ET.SubElement(raiz, f"{{{SVG}}}g", transform="translate(24 43) scale(.96)")
        for elemento in ET.fromstring(f'<g xmlns="{SVG}">{atras}</g>'):
            grupo.append(elemento)
        cerebro = deepcopy(original)
        if id_icone == "cruzeiro":
            for elemento in cerebro.iter():
                if elemento.get("fill") == "#F6A5BF":
                    elemento.set("fill", "#70AAF5")
                if elemento.get("stroke") == "#E07A9C":
                    elemento.set("stroke", "#3C7DCD")
        if id_icone == "mago":
            for elemento in cerebro.iter():
                if elemento.get("stroke") == "#1E5FA8":
                    elemento.set("stroke", "#3C354A")
        grupo.append(cerebro)
        for elemento in ET.fromstring(f'<g xmlns="{SVG}">{frente}</g>'):
            grupo.append(elemento)
        ET.indent(raiz)
        ET.ElementTree(raiz).write(ASSETS / f"avatar_{id_icone}.svg", encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    gerar()
