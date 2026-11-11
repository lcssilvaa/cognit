"""Falhas de transporte devem virar mensagens do jogo, sem derrubar a interface."""

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "jogo"))

from rede import ClienteSalas, ErroRede


class TestRede(unittest.IsolatedAsyncioTestCase):
    async def test_primeira_conexao_aguarda_servidor_sem_alongar_comandos_da_sala(self):
        cliente = ClienteSalas("https://salas.exemplo")
        with patch.object(ClienteSalas, "_desktop", return_value={}) as transporte:
            await cliente.requisitar("catalogo", {})
            self.assertEqual(transporte.call_args.args[2], 75)
            await cliente.requisitar("estado", {})
            self.assertEqual(transporte.call_args.args[2], 6)

    async def test_json_sem_objeto_e_tratado_como_erro_de_rede(self):
        cliente = ClienteSalas("http://jogo.local")
        for resposta in (None, [], "indisponível", True, 0):
            with self.subTest(resposta=resposta):
                with patch.object(ClienteSalas, "_desktop", return_value=resposta):
                    with self.assertRaisesRegex(ErroRede, "Resposta inválida"):
                        await cliente.requisitar("catalogo", {})

    async def test_timeout_e_apresentado_como_falha_de_conexao(self):
        cliente = ClienteSalas("http://jogo.local")
        with patch.object(ClienteSalas, "_desktop", side_effect=TimeoutError):
            with self.assertRaisesRegex(ErroRede, "Não foi possível conectar"):
                await cliente.requisitar("catalogo", {})
