"""Dois clientes HTTP reais contra um servidor local em porta temporária."""

import asyncio
import json
from pathlib import Path
import sys
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from servidor import ServidorSalas
from rede import ClienteSalas, ErroRede


class TestServidor(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.servidor = ServidorSalas(("127.0.0.1", 0), origens=("http://jogo.local",))
        self.thread = Thread(target=self.servidor.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.servidor.server_port}"
        self.cliente = ClienteSalas(self.url)

    async def asyncTearDown(self):
        await asyncio.to_thread(self.servidor.shutdown)
        self.servidor.server_close()
        self.thread.join(timeout=2)

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
