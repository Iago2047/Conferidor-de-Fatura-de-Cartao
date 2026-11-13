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

# ---------------------------------------------------------------------------
# Camada de Domínio: detecção de suspeitas (História 2)
# ---------------------------------------------------------------------------

def _normalizar(texto: str) -> str:
    """Ignora maiúsculas, minúsculas e espaços extras ao comparar estabelecimentos."""
    return " ".join(texto.split()).lower()


def detectar_duplicidade(lancamentos: List[Lancamento]) -> List[Suspeita]:
    """Aponta lançamentos com mesma data, mesmo estabelecimento e mesmo valor.

    O valor possivelmente indevido é o valor vezes as repetições além da primeira.
    """
    grupos = OrderedDict()
    for lancamento in lancamentos:
        chave = (lancamento.data, _normalizar(lancamento.estabelecimento), lancamento.valor)
        grupos.setdefault(chave, []).append(lancamento)

    suspeitas = []
    for grupo in grupos.values():
        repeticoes = len(grupo)
        if repeticoes < 2:
            continue
        primeiro = grupo[0]
        suspeitas.append(
            Suspeita(
                tipo=TIPO_DUPLICIDADE,
                motivo=f"Lançamento repetido {repeticoes} vezes na mesma data",
                estabelecimento=primeiro.estabelecimento.strip(),
                data=primeiro.data,
                valor_indevido=primeiro.valor * (repeticoes - 1),
            )
        )
    return suspeitas


def detectar_parcela_inconsistente(lancamentos: List[Lancamento]) -> List[Suspeita]:
    """Aponta parcelas fora do formato N/M, com N menor que 1 ou maior que M.

    Lançamentos sem parcela (compra à vista) não são suspeitos.
    """
    suspeitas = []
    for lancamento in lancamentos:
        parcela = (lancamento.parcela or "").strip()
        if not parcela:
            continue

        motivo = _motivo_parcela_invalida(parcela)
        if motivo:
            suspeitas.append(
                Suspeita(
                    tipo=TIPO_PARCELA,
                    motivo=motivo,
                    estabelecimento=lancamento.estabelecimento.strip(),
                    data=lancamento.data,
                    valor_indevido=lancamento.valor,
                )
            )
    return suspeitas


def _motivo_parcela_invalida(parcela: str) -> Optional[str]:
    """Devolve o motivo se a parcela for inválida, ou None se estiver correta."""
    partes = re.fullmatch(r"([0-9]+)/([0-9]+)", parcela)
    if not partes:
        return f"Formato de parcela inválido '{parcela}' (esperado N/M)"
    atual, total = int(partes.group(1)), int(partes.group(2))
    if total < 1:
        return f"Total de parcelas inválido em '{parcela}'"
    if atual < 1:
        return f"Número da parcela menor que 1 em '{parcela}'"
    if atual > total:
        return f"Parcela {atual} maior que o total de {total} parcelas"
    return None

# ---------------------------------------------------------------------------
# Camada de Domínio: relatório (História 3)
# ---------------------------------------------------------------------------

def _formatar_dinheiro(valor: Decimal) -> str:
    """449.9 -> 'R$ 449,90' (ponto nos milhares e vírgula nos centavos)."""
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {texto}"


def gerar_relatorio(
    lancamentos: List[Lancamento], suspeitas: List[Suspeita], avisos: List[str]
) -> str:
    """Monta o relatório em texto com o resumo, os avisos e as suspeitas."""
    total = sum((l.valor for l in lancamentos), Decimal("0"))
    linhas = [
        "RELATÓRIO DE CONFERÊNCIA DA FATURA",
        "==================================",
        f"Lançamentos lidos: {len(lancamentos)}",
        f"Valor total da fatura: {_formatar_dinheiro(total)}",
    ]

    if avisos:
        linhas += ["", "Avisos"]
        linhas += [f"- {aviso}" for aviso in avisos]

    linhas.append("")
    if not suspeitas:
        linhas.append("Nenhuma suspeita encontrada.")
    else:
        linhas += [f"Suspeitas encontradas ({len(suspeitas)})", "-" * 26]
        for numero, suspeita in enumerate(suspeitas, start=1):
            linhas += [
                f"{numero}. {suspeita.tipo}",
                f"   Motivo: {suspeita.motivo}",
                f"   Estabelecimento: {suspeita.estabelecimento}",
                f"   Data: {suspeita.data.strftime('%d/%m/%Y')}",
                f"   Valor possivelmente indevido: {_formatar_dinheiro(suspeita.valor_indevido)}",
            ]
        indevido = sum((s.valor_indevido for s in suspeitas), Decimal("0"))
        linhas += ["", f"Total possivelmente indevido: {_formatar_dinheiro(indevido)}"]

    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Camada de Aplicação: orquestrador
# ---------------------------------------------------------------------------

def conferir_fatura(caminho: str) -> str:
    """Executa as etapas na ordem e devolve o relatório em texto."""
    lancamentos, avisos = ler_fatura(caminho)

    if not lancamentos:
        linhas = ["Não foi possível conferir a fatura: nenhum lançamento válido foi lido."]
        linhas += [f"- {aviso}" for aviso in avisos]
        return "\n".join(linhas)

    suspeitas = detectar_duplicidade(lancamentos) + detectar_parcela_inconsistente(lancamentos)
    return gerar_relatorio(lancamentos, suspeitas, avisos)


# ---------------------------------------------------------------------------
# Camada de Apresentação: terminal
# ---------------------------------------------------------------------------

def main(argumentos: Optional[List[str]] = None) -> int:
    argumentos = sys.argv[1:] if argumentos is None else argumentos
    if len(argumentos) != 1:
        print("Uso: python conferidor_fatura.py fatura.csv", file=sys.stderr)
        return 2
    try:
        print(conferir_fatura(argumentos[0]))
    except (OSError, UnicodeDecodeError) as erro:
        print(f"Erro ao ler o arquivo: {erro}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

