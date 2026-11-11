"""Gera jogo/build/web, que pode ser publicado como site estático."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

RAIZ = Path(__file__).resolve().parent

comando = [
    sys.executable, "-m", "pygbag",
    "--build", "--no_opt",
    "--width", "390", "--height", "844",
    "--title", "Cognit",
    "--template", str(RAIZ / "web" / "cognit.tmpl"),
    "--icon", str(RAIZ / "jogo" / "assets" / "marca.png"),
    str(RAIZ / "jogo"),
]

def preparar_arquivos_web():
    """Expõe os recursos usados pelo navegador e a configuração pública da API."""
    shutil.copyfile(RAIZ / "web" / "campos.js", RAIZ / "jogo" / "build" / "web" / "campos.js")
    shutil.copyfile(RAIZ / "web" / "LICENSE-Pygbag.txt",
                    RAIZ / "jogo" / "build" / "web" / "LICENSE-Pygbag.txt")
    # O player nativo do navegador lê a trilha sem passar pelo mixer WebAssembly.
    assets_web = RAIZ / "jogo" / "build" / "web" / "assets"
    assets_web.mkdir(exist_ok=True)
    shutil.copyfile(RAIZ / "jogo" / "assets" / "musica_fundo.ogg",
                    assets_web / "musica_fundo.ogg")
    shutil.copyfile(RAIZ / "jogo" / "assets" / "Nunito-Regular.ttf",
                    assets_web / "Nunito-Regular.ttf")
    configuracao = json.loads((RAIZ / "web" / "configuracao.json").read_text(encoding="utf-8"))
    # Variável pública de build; não contém tokens nem segredos.
    configuracao["servidor"] = os.environ.get("COGNIT_SERVIDOR", "").strip()
    (RAIZ / "jogo" / "build" / "web" / "configuracao.js").write_text(
        "window.cognit_config = " + json.dumps(configuracao, ensure_ascii=True) + ";\n", encoding="utf-8")


if __name__ == "__main__":
    subprocess.run(comando, cwd=RAIZ, check=True)
    preparar_arquivos_web()
    print("\nExportação pronta em jogo/build/web.")
    print("Para testar o jogo e as salas: python servidor.py --port 8000")
