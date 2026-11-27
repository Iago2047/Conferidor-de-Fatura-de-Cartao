"""Testes do Conferidor de Fatura de Cartão, um por critério de aceitação

HU1 (Iago): validar a fatura, HU2 (Ives): detectar suspeitas, HU3 (Eric): gerar o relatório.
O nome do teste indica a história (hu) e o critério (ca), e os critérios estão em docs/sprint2/.

Para executar, na pasta onde está o conferidor_fatura.py:
    python -m unittest discover -s tests -v    (repositório)
    python -m unittest teste_conferidor_fatura -v    (os dois arquivos na mesma pasta)
"""

import os
import re
import tempfile
import unittest
from datetime import date
from decimal import Decimal

from conferidor_fatura import (
    Lancamento,
    Suspeita,
    detectar_duplicidade,
    detectar_parcela_inconsistente,
    gerar_relatorio,
    ler_fatura,
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


class TestHU1ValidarFatura(unittest.TestCase):
    """História 1: validar a fatura (arquivo CSV)."""

    COLUNAS = ("data", "estabelecimento", "valor", "parcela")
    LINHA_VALIDA = {
        "data": "06/10/2026",
        "estabelecimento": "Padoca",
        "valor": "49.90",
        "parcela": "",
    }

    def escrever_csv(self, conteudo):
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        caminho = os.path.join(pasta.name, "fatura.csv")
        with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
            arquivo.write(conteudo)
        return caminho

    def test_hu1_ca1_coluna_obrigatoria_ausente(self):
        """HU1 CA1: sem coluna obrigatória, não processa e informa qual falta."""
        for coluna in ("data", "estabelecimento", "valor"):
            with self.subTest(coluna_ausente=coluna):
                colunas = [c for c in self.COLUNAS if c != coluna]
                conteudo = (
                    ",".join(colunas)
                    + "\n"
                    + ",".join(self.LINHA_VALIDA[c] for c in colunas)
                    + "\n"
                )
                lancamentos, avisos = ler_fatura(self.escrever_csv(conteudo))
                self.assertEqual(lancamentos, [])
                self.assertTrue(
                    any(coluna in aviso.lower() for aviso in avisos),
                    f"nenhum aviso cita a coluna '{coluna}': {avisos}",
                )

    def test_hu1_ca2_sem_coluna_parcela(self):
        """HU1 CA2: sem a coluna parcela, processa e avisa que parcelas não foram conferidas."""
        conteudo = (
            "data,estabelecimento,valor\n"
            "06/10/2026,Padoca,49.90\n"
            "20/10/2026,Mercado Casa das Primas,230.10\n"
        )
        lancamentos, avisos = ler_fatura(self.escrever_csv(conteudo))
        self.assertEqual(len(lancamentos), 2)
        self.assertTrue(
            any("parcela" in aviso.lower() for aviso in avisos),
            f"nenhum aviso cita a conferência de parcelas: {avisos}",
        )

    def test_hu1_ca3_linha_invalida_ignorada(self):
        """HU1 CA3: linha com valor não numérico ou data inválida é ignorada e a linha é informada."""
        linhas_invalidas = {
            "valor não numérico": "06/10/2026,Padoca,abc,",
            "data inválida": "31/02/2026,Padoca,49.90,",
        }
        for descricao, linha_invalida in linhas_invalidas.items():
            with self.subTest(caso=descricao):
                conteudo = (
                    "data,estabelecimento,valor,parcela\n"
                    "05/10/2026,Padoca,49.90,\n"
                    + linha_invalida
                    + "\n"
                    "20/10/2026,Mercado Casa das Primas,230.10,\n"
                )
                lancamentos, avisos = ler_fatura(self.escrever_csv(conteudo))
                self.assertEqual([l.linha for l in lancamentos], [2, 4])
                self.assertTrue(
                    any("linha 3" in aviso.lower() for aviso in avisos),
                    f"nenhum aviso cita a linha 3: {avisos}",
                )


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
