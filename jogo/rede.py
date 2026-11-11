"""Cliente HTTP assíncrono. Desktop usa uma thread; navegador usa fetch.

Nenhuma requisição bloqueia o desenho do jogo. Tokens viajam no corpo JSON.
"""

import asyncio
import json
import sys
import uuid


class ErroRede(Exception):
    pass


class ClienteSalas:
    def __init__(self, endereco):
        self.endereco = endereco.strip().rstrip("/")
        if not self.endereco.startswith(("http://", "https://")) or any(c.isspace() for c in self.endereco):
            raise ErroRede("Informe o servidor com http:// ou https://.")

    async def requisitar(self, acao, dados):
        url = f"{self.endereco}/api/{acao}"
        corpo = json.dumps(dados)  # Escapes Unicode também atravessam a ponte web.
        # O catálogo é a primeira conexão e pode precisar despertar o Render Free.
        espera = 75 if acao == "catalogo" else 6
        try:
            if sys.platform == "emscripten":
                resposta = await self._web(url, corpo, espera)
            else:
                resposta = await asyncio.to_thread(self._desktop, url, corpo, espera)
        except ErroRede:
            raise
        except Exception as erro:
            raise ErroRede("Não foi possível conectar. Tente novamente em instantes.") from erro
        if not isinstance(resposta, dict):
            raise ErroRede("Resposta inválida do servidor. Tente novamente em instantes.")
        if "erro" in resposta:
            raise ErroRede(resposta["erro"])
        return resposta

    @staticmethod
    def _desktop(url, corpo, espera=6):
        # urllib não é importado no WebAssembly.
        from urllib.error import HTTPError
        from urllib.request import Request, urlopen

        pedido = Request(url, corpo.encode("utf-8"), {"Content-Type": "application/json"})
        try:
            resposta = urlopen(pedido, timeout=espera)
        except HTTPError as erro:
            resposta = erro
        with resposta:
            return json.loads(resposta.read().decode("utf-8"))

    @staticmethod
    async def _web(url, corpo, espera=6):
        import platform

        id_pedido = uuid.uuid4().hex
        platform.window.cognit_requisitar(id_pedido, url, corpo, espera)
        try:
            while True:
                resultado = platform.window.cognit_resultado(id_pedido)
                if resultado:
                    return json.loads(str(resultado))
                await asyncio.sleep(0.03)
        finally:
            platform.window.cognit_cancelar(id_pedido)
