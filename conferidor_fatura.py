"""Conferidor de Fatura de Cartão.

Lê um CSV com os lançamentos de uma fatura, aponta suspeitas de cobrança
indevida (duplicidades e parcelas inconsistentes) e gera um relatório em texto.

Arquitetura em camadas (ver docs/arquitetura.md):
- Apresentação: main()
- Aplicação:    conferir_fatura()
- Dados:        ler_fatura()
- Domínio:      detectar_duplicidade(), detectar_parcela_inconsistente(),
                gerar_relatorio() e as entidades Lancamento e Suspeita

Uso:
    python conferidor_fatura.py fatura.csv

Formato do CSV: UTF-8, separado por vírgula, com cabeçalho. Colunas obrigatórias:
data, estabelecimento e valor. Coluna opcional: parcela (por exemplo, 3/12).
Datas em DD/MM/AAAA e valores com ponto decimal (49.90).
"""

import csv
import re
import sys
from collections import OrderedDict
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Tuple

COLUNAS_OBRIGATORIAS = ("data", "estabelecimento", "valor")
TIPO_DUPLICIDADE = "Duplicidade"
TIPO_PARCELA = "Parcela inconsistente"


# ---------------------------------------------------------------------------
# Entidades (Domínio)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Lancamento:
    """Uma linha da fatura."""

    data: date
    estabelecimento: str
    valor: Decimal
    parcela: Optional[str] = None
    linha: int = 0  # número da linha no arquivo (o cabeçalho é a linha 1)


@dataclass(frozen=True)
class Suspeita:
    """Uma cobrança que o sistema considera suspeita."""

    tipo: str
    motivo: str
    estabelecimento: str
    data: date
    valor_indevido: Decimal


# ---------------------------------------------------------------------------
# Camada de Dados: leitura e validação do CSV (História 1)
# ---------------------------------------------------------------------------

def ler_fatura(caminho: str) -> Tuple[List[Lancamento], List[str]]:
    """Lê o CSV e devolve (lancamentos, avisos).

    - Sem coluna obrigatória: não processa e avisa qual coluna falta.
    - Sem coluna parcela: processa e avisa que as parcelas não foram conferidas.
    - Linha com data ou valor inválido: ignora a linha e avisa o número dela.
    """
    avisos: List[str] = []
    lancamentos: List[Lancamento] = []

    # utf-8-sig também lê arquivos salvos pelo Excel, que podem ter BOM
    with open(caminho, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if not leitor.fieldnames:
            return [], ["O arquivo está vazio."]

        # ignora maiúsculas e espaços nos nomes das colunas
        leitor.fieldnames = [nome.strip().lower() for nome in leitor.fieldnames]

        ausentes = [c for c in COLUNAS_OBRIGATORIAS if c not in leitor.fieldnames]
        if ausentes:
            for coluna in ausentes:
                avisos.append(
                    f"Coluna obrigatória ausente: '{coluna}'. "
                    "A fatura não foi processada."
                )
            return [], avisos

        tem_parcela = "parcela" in leitor.fieldnames
        if not tem_parcela:
            avisos.append(
                "Coluna 'parcela' ausente: a conferência de parcelas não foi feita."
            )

        for registro in leitor:
            numero_linha = leitor.line_num
            try:
                lancamentos.append(_converter_linha(registro, numero_linha, tem_parcela))
            except ValueError as erro:
                avisos.append(f"Linha {numero_linha} ignorada: {erro}.")

    return lancamentos, avisos


def _converter_linha(registro: dict, numero_linha: int, tem_parcela: bool) -> Lancamento:
    """Converte uma linha do CSV em Lancamento. Levanta ValueError se for inválida."""
    texto_data = (registro.get("data") or "").strip()
    estabelecimento = (registro.get("estabelecimento") or "").strip()
    texto_valor = (registro.get("valor") or "").strip()

    try:
        data = datetime.strptime(texto_data, "%d/%m/%Y").date()
    except ValueError:
        raise ValueError(f"data inválida '{texto_data}' (esperado DD/MM/AAAA)") from None

    if not estabelecimento:
        raise ValueError("estabelecimento vazio")

    try:
        valor = Decimal(texto_valor)
    except InvalidOperation:
        raise ValueError(f"valor não numérico '{texto_valor}'") from None
    if not valor.is_finite():
        raise ValueError(f"valor não numérico '{texto_valor}'")

    parcela = None
    if tem_parcela:
        parcela = (registro.get("parcela") or "").strip() or None

    return Lancamento(
        data=data,
        estabelecimento=estabelecimento,
        valor=valor,
        parcela=parcela,
        linha=numero_linha,
    )


