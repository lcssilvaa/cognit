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
    print("\nExportação pronta em jogo/build/web.")
    print("Para testar: python -m http.server 8000 --directory jogo/build/web")
