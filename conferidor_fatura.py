"""Conferidor de Fatura de Cartão

Lê a fatura detalhada em CSV, aponta lançamentos suspeitos (duplicidade e parcela inconsistente) e gera um relatório em texto
"""

import sys
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class Lancamento:
    """Uma linha da fatura 'linha' é o numero da linha no CSV """

    data: date
    estabelecimento: str
    valor: Decimal
    parcela: Optional[str] = None
    linha: int = 0


@dataclass
class Suspeita:
    """Um lançamento suspeito, com o motivo e o valor posivelmente indevido"""

    tipo: str
    motivo: str
    estabelecimento: str
    data: date
    valor_indevido: Decimal


def ler_fatura(caminho):
    """História 1: lê o CSV e devolve"""
    raise NotImplementedError("ler_fatura ainda não foi implementada")


def detectar_duplicidade(lancamentos):
    """História 2: devolve a lista de Suspeita do tipoduplicidade"""
    raise NotImplementedError("detectar_duplicidade ainda não foi implementada")


def detectar_parcela_inconsistente(lancamentos):
    """História 2: devolve a lista de Suspeita do tipo 'Parcela inconsistente'."""
    raise NotImplementedError("detectar_parcela_inconsistente ainda não foi implementada")


def gerar_relatorio(lancamentos, suspeitas, avisos):
    """História 3 : devolve o relatório em texto"""
    raise NotImplementedError("gerar_relatorio ainda não foi implementada")


def main(argumentos=None):
    argumentos = sys.argv[1:] if argumentos is None else argumentos
    if len(argumentos) != 1:
        print("Uso: python conferidor_fatura.py caminho_da_fatura.csv")
        return 1

    lancamentos, avisos = ler_fatura(argumentos[0])
    suspeitas = detectar_duplicidade(lancamentos) + detectar_parcela_inconsistente(lancamentos)
    print(gerar_relatorio(lancamentos, suspeitas, avisos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
