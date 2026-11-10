"""Servidor de salas para amigos. Execute: python servidor.py --host 0.0.0.0.

Não precisa de Pygame. Mantém salas em memória e atende desktop e navegador.
Para internet, execute uma única instância atrás de um proxy HTTPS.
"""

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
from urllib.parse import quote, unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent / "jogo"))

from salas import ErroSala, GerenciadorSalas

WEB = Path(__file__).resolve().parent / "jogo" / "build" / "web"


class ServidorSalas(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, endereco, origens=("*",), gerenciador=None, diretorio_web=WEB):
        self.diretorio_web = Path(diretorio_web).resolve()
        super().__init__(endereco, Requisicao)
        self.gerenciador = gerenciador or GerenciadorSalas()
        self.origens = origens


class Requisicao(SimpleHTTPRequestHandler):
    """Adaptador HTTP: valida o JSON e delega as regras ao gerenciador."""

    def __init__(self, pedido, endereco, servidor):
        super().__init__(pedido, endereco, servidor, directory=str(servidor.diretorio_web))

    def log_message(self, formato, *args):
        # Não registra tokens nem respostas dos jogadores.
        pass

    def _origem_permitida(self):
        origem = self.headers.get("Origin")
        return not origem or "*" in self.server.origens or origem in self.server.origens

    def _responder(self, status, dados=None):
        corpo = json.dumps(dados or {}, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        origem = self.headers.get("Origin")
        if "*" in self.server.origens:
            self.send_header("Access-Control-Allow-Origin", "*")
        elif origem in self.server.origens:
            self.send_header("Access-Control-Allow-Origin", origem)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(corpo)

    def do_OPTIONS(self):
        self._responder(200 if self._origem_permitida() else 403)

    def do_GET(self):
        caminho = urlsplit(self.path).path
        if caminho == "/saude":
            self._responder(200, {"ok": True})
        elif caminho == "/" and not (self.server.diretorio_web / "index.html").is_file():
            self._responder(200, {
                "ok": True,
                "servico": "Servidor de salas do Cognit",
                "mensagem": (
                    "O servidor está funcionando. Para jogar, execute o comando abaixo "
                    "em outro terminal e escolha Jogar com amigos. A conexão é configurada "
                    "em jogo/config.py ou na variável COGNIT_SERVIDOR."
                ),
                "abrir_jogo": "python jogo/main.py",
                "verificar_servidor": "/saude",
            })
        else:
            self._servir_arquivo(caminho)

    def do_HEAD(self):
        self.do_GET()

    def _servir_arquivo(self, caminho):
        # Publica somente arquivos do build, sem listar pastas nem expor o código-fonte.
        relativo = unquote(caminho).lstrip("/") or "index.html"
        arquivo = (self.server.diretorio_web / relativo).resolve()
        if (not arquivo.is_relative_to(self.server.diretorio_web)
                or not arquivo.is_file()
                or any(parte.startswith(".") for parte in Path(relativo).parts)):
            self._responder(404, {"erro": "Endereço não encontrado."})
            return
        self.path = "/" + quote(relativo)
        if self.command == "HEAD":
            super().do_HEAD()
        else:
            super().do_GET()

    def do_POST(self):
        self.connection.settimeout(10)
        if not self._origem_permitida():
            self._responder(403, {"erro": "Origem não autorizada neste servidor."})
            return
        acoes = {"catalogo", "criar", "entrar", "estado", "iniciar", "proxima", "responder", "dica", "pronto", "sair"}
        acao = self.path.removeprefix("/api/")
        if not self.path.startswith("/api/") or acao not in acoes:
            self._responder(404, {"erro": "Ação não encontrada."})
            return
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            if not 0 < tamanho <= 4096:
                raise ErroSala("Requisição vazia ou muito grande.")
            dados = json.loads(self.rfile.read(tamanho).decode("utf-8"))
            if not isinstance(dados, dict):
                raise ErroSala("Envie um objeto JSON.")
            resposta = self.server.gerenciador.executar(acao, dados)
        except (ValueError, UnicodeError) as erro:
            mensagem = str(erro) if isinstance(erro, ErroSala) else "JSON ou dados inválidos."
            self._responder(400, {"erro": mensagem})
        else:
            self._responder(200, resposta)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8765")))
    parser.add_argument("--web", type=Path, default=WEB, help="Diretório do jogo exportado.")
    parser.add_argument("--origem", action="append", help="Origem web permitida; pode repetir.")
    args = parser.parse_args()
    with ServidorSalas((args.host, args.port), args.origem or ("*",), diretorio_web=args.web) as servidor:
        print(f"Servidor escutando em {args.host}:{servidor.server_port}", flush=True)
        if (servidor.diretorio_web / "index.html").is_file():
            print("Jogo e API de salas disponíveis no mesmo endereço.", flush=True)
        print("Para abrir o jogo, execute em outro terminal: python jogo/main.py")
        print("No jogo, escolha Jogar com amigos. A conexão é configurada em jogo/config.py.")
        print("Salas ficam em memória. Ctrl+C encerra o servidor.")
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
