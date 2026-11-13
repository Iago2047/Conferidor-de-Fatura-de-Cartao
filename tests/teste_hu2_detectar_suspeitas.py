"""Testes da História 2 (Ives): detectar suspeitas.

Cada teste verifica um critério de aceitação de docs/sprint2_historias.md.
O nome do teste indica a história (hu) e o critério (ca).

Convenções do trio:
- Lancamento: data (datetime.date), estabelecimento (str), valor (Decimal),
  parcela (str ou None) e linha (int).
- Suspeita: tipo, motivo, estabelecimento, data e valor_indevido (Decimal).
- Tipos de suspeita: "Duplicidade" e "Parcela inconsistente".
- As funções de detecção recebem uma lista de Lancamento e devolvem uma lista de Suspeita.

Para executar: python -m unittest teste_hu2_detectar_suspeitas -v
"""

import unittest
from datetime import date
from decimal import Decimal

from conferidor_fatura import (
    Lancamento,
    detectar_duplicidade,
    detectar_parcela_inconsistente,
)


def criar_lancamento(dia, mes, estabelecimento, valor, parcela=None, linha=2):
    return Lancamento(
        data=date(2026, mes, dia),
        estabelecimento=estabelecimento,
        valor=Decimal(valor),
        parcela=parcela,
        linha=linha,
    )


def fatura_exemplo():
    """Os 4 lançamentos do exemplo das histórias (total: R$ 449,90)."""
    return [
        criar_lancamento(6, 10, "Padoca", "49.90", linha=2),
        criar_lancamento(6, 10, "Padoca", "49.90", linha=3),
        criar_lancamento(15, 10, "Loja Todo Poderoso Timão", "120.00", "13/12", linha=4),
        criar_lancamento(20, 10, "Mercado Casa das Primas", "230.10", linha=5),
    ]


class TestHU2DetectarSuspeitas(unittest.TestCase):
    """História 2: detectar duplicidades e parcelas inconsistentes."""

    def test_hu2_ca1_duplicidade_detectada(self):
        """HU2 CA1: lançamentos iguais (data, estabelecimento e valor) geram suspeita de duplicidade."""
        suspeitas = detectar_duplicidade(fatura_exemplo())
        self.assertEqual(len(suspeitas), 1)
        suspeita = suspeitas[0]
        self.assertEqual(suspeita.tipo, "Duplicidade")
        self.assertEqual(suspeita.estabelecimento.strip().lower(), "padoca")
        self.assertEqual(suspeita.data, date(2026, 10, 6))
        self.assertEqual(suspeita.valor_indevido, Decimal("49.90"))
        self.assertTrue(suspeita.motivo)

        with self.subTest("ignora maiúsculas, minúsculas e espaços extras"):
            lancamentos = [
                criar_lancamento(6, 10, "Padoca", "49.90", linha=2),
                criar_lancamento(6, 10, "  PADOCA ", "49.90", linha=3),
            ]
            self.assertEqual(len(detectar_duplicidade(lancamentos)), 1)

        with self.subTest("três repetições: valor indevido são as repetições além da primeira"):
            lancamentos = [
                criar_lancamento(6, 10, "Padoca", "49.90", linha=2),
                criar_lancamento(6, 10, "Padoca", "49.90", linha=3),
                criar_lancamento(6, 10, "Padoca", "49.90", linha=4),
            ]
            suspeitas = detectar_duplicidade(lancamentos)
            self.assertEqual(len(suspeitas), 1)
            self.assertEqual(suspeitas[0].valor_indevido, Decimal("99.80"))

    def test_hu2_ca2_parcela_invalida_detectada(self):
        """HU2 CA2: parcela fora do formato N/M, com N menor que 1 ou maior que M, gera suspeita."""
        for parcela in ("13/12", "0/12", "3-12", "abc"):
            with self.subTest(parcela_invalida=parcela):
                lancamentos = [
                    criar_lancamento(15, 10, "Loja Todo Poderoso Timão", "120.00", parcela)
                ]
                suspeitas = detectar_parcela_inconsistente(lancamentos)
                self.assertEqual(len(suspeitas), 1)
                self.assertEqual(suspeitas[0].tipo, "Parcela inconsistente")
                self.assertEqual(suspeitas[0].valor_indevido, Decimal("120.00"))
                self.assertTrue(suspeitas[0].motivo)

        for parcela in ("3/12", "12/12", None):
            with self.subTest(parcela_valida=parcela):
                lancamentos = [
                    criar_lancamento(15, 10, "Loja Todo Poderoso Timão", "120.00", parcela)
                ]
                self.assertEqual(detectar_parcela_inconsistente(lancamentos), [])

    def test_hu2_ca3_datas_diferentes_nao_e_duplicidade(self):
        """HU2 CA3: mesmo estabelecimento e valor em datas diferentes (assinatura mensal) não é duplicidade."""
        lancamentos = [
            criar_lancamento(5, 10, "Streaming Filmes", "39.90", linha=2),
            criar_lancamento(5, 11, "Streaming Filmes", "39.90", linha=3),
        ]
        self.assertEqual(detectar_duplicidade(lancamentos), [])


if __name__ == "__main__":
    unittest.main()
