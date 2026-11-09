"""Testes da História 3: gerar o relatório

Cada teste verifica um critério de aceitação de docs/sprint2_historias.md
"""

import re
import unittest
from datetime import date
from decimal import Decimal

from conferidor_fatura import Lancamento, Suspeita, gerar_relatorio


def criar_lancamento(dia, estabelecimento, valor, parcela=None, linha=2):
    return Lancamento(
        data=date(2026, 10, dia),
        estabelecimento=estabelecimento,
        valor=Decimal(valor),
        parcela=parcela,
        linha=linha,
    )


def fatura_exemplo():
    """Os 4 lançamentos do exemplo das histórias (total: R$ 449,90)."""
    return [
        criar_lancamento(6, "Padoca", "49.90", linha=2),
        criar_lancamento(6, "Padoca", "49.90", linha=3),
        criar_lancamento(15, "Loja Todo Poderoso Timão", "120.00", "13/12", linha=4),
        criar_lancamento(20, "Mercado Casa das Primas", "230.10", linha=5),
    ]


def suspeitas_exemplo():
    """As 2 suspeitas do exemplo das histórias."""
    return [
        Suspeita(
            tipo="Duplicidade",
            motivo="Lançamento repetido na mesma data",
            estabelecimento="Padoca",
            data=date(2026, 10, 6),
            valor_indevido=Decimal("49.90"),
        ),
        Suspeita(
            tipo="Parcela inconsistente",
            motivo="Parcela 13 maior que o total de 12 parcelas",
            estabelecimento="Loja Todo Poderoso Timão",
            data=date(2026, 10, 15),
            valor_indevido=Decimal("120.00"),
        ),
    ]


class TestHU3GerarRelatorio(unittest.TestCase):
    """História 3: gerar o relatório em texto"""

    def test_hu3_ca1_resumo_da_fatura(self):
        """HU3 CA1: o relatório informa a quantidade de lançamentos e o total"""
        relatorio = gerar_relatorio(fatura_exemplo(), suspeitas_exemplo(), [])
        self.assertIn("R$ 449,90", relatorio)
        self.assertRegex(relatorio, re.compile(r"lan[çc]amentos[^\n]*\b4\b", re.IGNORECASE))

    def test_hu3_ca2_detalhes_da_suspeita(self):
        """HU3 CA2: cada suspeita traz tipo, motivo, estabelecimento, data e valor possivelmente indevido"""
        relatorio = gerar_relatorio(fatura_exemplo(), suspeitas_exemplo(), [])
        self.assertIn("Suspeitas encontradas", relatorio)
        self.assertIn("Duplicidade", relatorio)
        self.assertIn("Lançamento repetido na mesma data", relatorio)
        self.assertIn("Padoca", relatorio)
        self.assertIn("06/10/2026", relatorio)
        self.assertIn("R$ 49,90", relatorio)
        self.assertIn("Parcela inconsistente", relatorio)
        self.assertIn("Parcela 13 maior que o total de 12 parcelas", relatorio)
        self.assertIn("Loja Todo Poderoso Timão", relatorio)
        self.assertIn("15/10/2026", relatorio)
        self.assertIn("R$ 120,00", relatorio)

    def test_hu3_ca3_nenhuma_suspeita(self):
        """HU3 CA3: sem suspeitas, informa isso explicitamente e não mostra a seção de suspeitas"""
        relatorio = gerar_relatorio(fatura_exemplo(), [], [])
        self.assertIn("nenhuma suspeita", relatorio.lower())
        self.assertNotIn("Suspeitas encontradas", relatorio)


if __name__ == "__main__":
    unittest.main()
