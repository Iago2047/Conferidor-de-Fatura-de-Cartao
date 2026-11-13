"""Testes da História 1 (Iago): validar a fatura.

Cada teste verifica um critério de aceitação de docs/sprint2_historias.md.
O nome do teste indica a história (hu) e o critério (ca).

Convenções do trio:
- ler_fatura(caminho) devolve (lancamentos, avisos); avisos é uma lista de textos.
- Lancamento tem o atributo linha (número da linha no arquivo; o cabeçalho é a linha 1).
- O CSV é lido em UTF-8, com vírgula como separador e datas DD/MM/AAAA.

Para executar: python -m unittest teste_hu1_validar_fatura -v
"""

import os
import tempfile
import unittest

from conferidor_fatura import ler_fatura


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


if __name__ == "__main__":
    unittest.main()
