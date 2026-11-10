"""Gera jogo/build/web, que pode ser publicado como site estático."""

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

if __name__ == "__main__":
    subprocess.run(comando, cwd=RAIZ, check=True)
    shutil.copyfile(RAIZ / "web" / "LICENSE-Pygbag.txt",
                    RAIZ / "jogo" / "build" / "web" / "LICENSE-Pygbag.txt")
    # O player nativo do navegador lê a trilha sem passar pelo mixer WebAssembly.
    assets_web = RAIZ / "jogo" / "build" / "web" / "assets"
    assets_web.mkdir(exist_ok=True)
    shutil.copyfile(RAIZ / "jogo" / "assets" / "musica_fundo.ogg",
                    assets_web / "musica_fundo.ogg")
    print("\nExportação pronta em jogo/build/web.")
    print("Para testar o jogo e as salas: python servidor.py --port 8000")
