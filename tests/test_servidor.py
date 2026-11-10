"""Dois clientes HTTP reais contra um servidor local em porta temporária."""

import asyncio
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from servidor import ServidorSalas
from rede import ClienteSalas, ErroRede


class TestServidor(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.web_temporaria = TemporaryDirectory()
        self.web = Path(self.web_temporaria.name)
        self.servidor = ServidorSalas(("127.0.0.1", 0), origens=("http://jogo.local",),
                                     diretorio_web=self.web)
        self.thread = Thread(target=self.servidor.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.servidor.server_port}"
        self.cliente = ClienteSalas(self.url)

    async def asyncTearDown(self):
        await asyncio.to_thread(self.servidor.shutdown)
        self.servidor.server_close()
        self.thread.join(timeout=2)
        self.web_temporaria.cleanup()

    async def test_jogo_arquivos_e_api_no_mesmo_endereco(self):
        pagina = b"<!doctype html><title>Cognit</title>"
        (self.web / "index.html").write_bytes(pagina)
        (self.web / "assets").mkdir()
        (self.web / "assets" / "musica_fundo.ogg").write_bytes(b"OggS")

        def verificar():
            with urlopen(self.url + "/?origem=teste", timeout=3) as resposta:
                self.assertEqual(resposta.read(), pagina)
                self.assertEqual(resposta.headers.get_content_type(), "text/html")
            with urlopen(self.url + "/assets/musica_fundo.ogg", timeout=3) as resposta:
                self.assertEqual(resposta.read(), b"OggS")
            with urlopen(Request(self.url + "/", method="HEAD"), timeout=3) as resposta:
                self.assertEqual(int(resposta.headers["Content-Length"]), len(pagina))
                self.assertEqual(resposta.read(), b"")
            with urlopen(self.url + "/saude", timeout=3) as resposta:
                self.assertEqual(json.loads(resposta.read()), {"ok": True})
            with urlopen(Request(self.url + "/saude", method="HEAD"), timeout=3) as resposta:
                self.assertEqual(resposta.status, 200)
                self.assertEqual(resposta.read(), b"")

        await asyncio.to_thread(verificar)
        catalogo = await self.cliente.requisitar("catalogo", {})
        self.assertTrue(catalogo["temas"])

    async def test_arquivos_privados_e_listagem_nao_sao_publicados(self):
        (self.web / ".env").write_text("segredo", encoding="utf-8")
        (self.web / "assets").mkdir()

        def verificar():
            for caminho in ("/.env", "/assets/", "/../servidor.py", "/%2e%2e/servidor.py",
                            "/%252e%252e/servidor.py", "/servidor.py"):
                with self.subTest(caminho=caminho), self.assertRaises(HTTPError) as erro:
                    urlopen(self.url + caminho, timeout=3)
                self.assertEqual(erro.exception.code, 404)
                erro.exception.close()

        await asyncio.to_thread(verificar)

    async def test_criar_entrar_iniciar_responder_e_ver_placar(self):
        catalogo = await self.cliente.requisitar("catalogo", {})
        self.assertEqual([t["id"] for t in catalogo["temas"]], ["tecnologia", "ux_design"])
        host = await self.cliente.requisitar("criar", {"nome": "Ana", "tema": "tecnologia", "icone": "hyrule"})
        amigo = await self.cliente.requisitar("entrar", {"nome": "Bia", "codigo": host["codigo"]})
        sessao = {"codigo": host["codigo"], "token": host["token"]}
        outra = {"codigo": host["codigo"], "token": amigo["token"]}
        estado = await self.cliente.requisitar("iniciar", sessao)
        self.assertEqual(estado["nome_tema"], "Tecnologia")
        self.assertEqual(estado["voce"]["icone"], "hyrule")
        await asyncio.gather(
            self.cliente.requisitar("responder", {**sessao, "indice": 0, "alternativa": 1}),
            self.cliente.requisitar("responder", {**outra, "indice": 0, "alternativa": 0}),
        )
        placar = await self.cliente.requisitar("estado", sessao)
        self.assertEqual(placar["fase"], "placar")
        self.assertEqual(len(placar["jogadores"]), 2)
        self.assertGreater(placar["voce"]["pontos"], 0)

    async def test_erro_do_servidor_chega_ao_cliente(self):
        with self.assertRaisesRegex(ErroRede, "Sala não encontrada"):
            await self.cliente.requisitar("entrar", {"nome": "Ana", "codigo": "000000"})

    async def test_cors_e_json_invalido(self):
        def requisitar(corpo, origem):
            pedido = Request(self.url + "/api/criar", corpo, {"Origin": origem, "Content-Type": "application/json"})
            try:
                resposta = urlopen(pedido, timeout=3)
            except HTTPError as erro:
                resposta = erro
            with resposta:
                return resposta.status, dict(resposta.headers), json.loads(resposta.read())
        status, headers, dados = await asyncio.to_thread(requisitar, b"{", "http://jogo.local")
        self.assertEqual(status, 400)
        self.assertIn("erro", dados)
        self.assertEqual(headers["Access-Control-Allow-Origin"], "http://jogo.local")
        status, _, _ = await asyncio.to_thread(requisitar, b"{}", "http://outra.local")
        self.assertEqual(status, 403)
