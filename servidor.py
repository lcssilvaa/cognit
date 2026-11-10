"""Servidor de salas para amigos. Execute: python servidor.py --host 0.0.0.0.

Não precisa de Pygame. Mantém salas em memória e atende desktop e navegador.
Para internet, execute uma única instância atrás de um proxy HTTPS.
"""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "jogo"))

from salas import ErroSala, GerenciadorSalas


class ServidorSalas(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, endereco, origens=("*",), gerenciador=None):
        super().__init__(endereco, Requisicao)
        self.gerenciador = gerenciador or GerenciadorSalas()
        self.origens = origens


class Requisicao(BaseHTTPRequestHandler):
    """Adaptador HTTP: valida o JSON e delega as regras ao gerenciador."""

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
        self.wfile.write(corpo)

    def do_OPTIONS(self):
        self._responder(200 if self._origem_permitida() else 403)

    def do_GET(self):
        caminho = self.path.partition("?")[0]
        if caminho == "/":
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
        elif caminho == "/saude":
            self._responder(200, {"ok": True})
        else:
            self._responder(404, {"erro": "Endereço não encontrado."})

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
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--origem", action="append", help="Origem web permitida; pode repetir.")
    args = parser.parse_args()
    with ServidorSalas((args.host, args.port), args.origem or ("*",)) as servidor:
        host_acesso = "localhost" if args.host == "0.0.0.0" else args.host
        print(f"Servidor de salas em http://{host_acesso}:{servidor.server_port}")
        print("Para abrir o jogo, execute em outro terminal: python jogo/main.py")
        print("No jogo, escolha Jogar com amigos. A conexão é configurada em jogo/config.py.")
        print("Salas ficam em memória. Ctrl+C encerra o servidor.")
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
