## História 2: Detectar suspeitas

**Como** consumidor que confere a fatura,
**quero** que o sistema aponte lançamentos duplicados e parcelas inconsistentes,
**para** decidir quais cobranças contestar no banco.

### Critérios de aceitação

| Critério | Verificação | Teste |
|----------|-------------|-------|
| CA1 | Dois ou mais lançamentos com mesma data, mesmo estabelecimento (sem diferenciar maiúsculas, minúsculas e espaços extras) e mesmo valor: o sistema aponta duplicidade. O valor possivelmente indevido é o valor vezes as repetições além da primeira (dois de 49.90 resultam em 49.90, três resultam em 99.80). | `test_hu2_ca1_duplicidade_detectada` |
| CA2 | Parcela inválida (formato diferente de N/M, N menor que 1 ou N maior que M, como 13/12): aponta parcela inconsistente com o motivo e o valor do lançamento. | `test_hu2_ca2_parcela_invalida_detectada` |
| CA3 | Mesmo estabelecimento e valor em datas diferentes (assinatura mensal): não é duplicidade. | `test_hu2_ca3_datas_diferentes_nao_e_duplicidade` |

### Entregáveis

| Entrega | Detalhe |
|---------|---------|
| Funções | `detectar_duplicidade` e `detectar_parcela_inconsistente` (esqueletos com `NotImplementedError`) |
| Testes | Classe `TestHU2` com os 3 testes acima |
| Documento | Esta seção em `docs/sprint2_historias.md` |
| Commit | Um commit, com mensagem em português |

### Decisões de projeto

- **Chave de duplicidade:** `(data, estabelecimento normalizado, valor)`. A normalização remove espaços nas pontas, colapsa espaços internos e converte para minúsculas.
- **Valor possivelmente indevido:** `valor × (repetições − 1)`. Exemplos: 2 × 49.90 → 49.90; 3 × 49.90 → 99.80.
- **Assinatura mensal não é duplicidade:** a data faz parte da chave, então mesmo estabelecimento e valor em datas diferentes não são agrupados (CA3).
- **Parcela válida:** string no formato `N/M`, com `N` e `M` inteiros, `N >= 1` e `N <= M`. Qualquer outra coisa é inconsistente.
- **Lançamento sem parcela** (`None` ou vazio) é compra à vista, então não é analisado.
- **Motivos possíveis** da parcela inconsistente: `formato inválido`, `parcela menor que 1`, `parcela maior que o total`.
- **Retorno:** listas de dicionários (vazia quando não há suspeita), para a interface/relatório decidir como exibir.

### Contrato das funções

**Entrada:** lista de lançamentos, cada um um dicionário com as chaves `data` (`"AAAA-MM-DD"`), `estabelecimento` (str), `valor` (float) e `parcela` (str ou `None`).

```python
detectar_duplicidade(lancamentos) -> list[dict]
# [{"estabelecimento": "netflix", "data": "2026-10-05",
#   "valor": 49.90, "repeticoes": 2, "valor_indevido": 49.90}]

detectar_parcela_inconsistente(lancamentos) -> list[dict]
# [{"estabelecimento": "Loja X", "parcela": "13/12",
#   "valor": 120.00, "motivo": "parcela maior que o total"}]
```

> Ajustar os nomes das chaves se o modelo de lançamento da Sprint 1 for diferente.

### Esqueletos (`src/suspeitas.py`)

```python
def detectar_duplicidade(lancamentos):
    """CA1/CA3: aponta lançamentos com mesma data, estabelecimento
    (normalizado) e valor. Valor indevido = valor * (repeticoes - 1)."""
    raise NotImplementedError("HU2 CA1/CA3: detectar_duplicidade")


def detectar_parcela_inconsistente(lancamentos):
    """CA2: aponta parcelas fora do formato N/M, com N < 1 ou N > M."""
    raise NotImplementedError("HU2 CA2: detectar_parcela_inconsistente")
```

### Testes (`tests/test_sprint2.py`)

```python
import pytest

from src.suspeitas import detectar_duplicidade, detectar_parcela_inconsistente


class TestHU2:
    def test_hu2_ca1_duplicidade_detectada(self):
        lancamentos = [
            {"data": "2026-10-05", "estabelecimento": "Netflix",
             "valor": 49.90, "parcela": None},
            {"data": "2026-10-05", "estabelecimento": "  NETFLIX ",
             "valor": 49.90, "parcela": None},
        ]
        resultado = detectar_duplicidade(lancamentos)

        assert len(resultado) == 1
        assert resultado[0]["repeticoes"] == 2
        assert resultado[0]["valor_indevido"] == pytest.approx(49.90)

    def test_hu2_ca2_parcela_invalida_detectada(self):
        lancamentos = [
            {"data": "2026-10-10", "estabelecimento": "Loja X",
             "valor": 120.00, "parcela": "13/12"},
            {"data": "2026-10-11", "estabelecimento": "Loja Y",
             "valor": 80.00, "parcela": "3/10"},
        ]
        resultado = detectar_parcela_inconsistente(lancamentos)

        assert len(resultado) == 1
        assert resultado[0]["parcela"] == "13/12"
        assert resultado[0]["valor"] == pytest.approx(120.00)
        assert resultado[0]["motivo"]

    def test_hu2_ca3_datas_diferentes_nao_e_duplicidade(self):
        lancamentos = [
            {"data": "2026-09-05", "estabelecimento": "Spotify",
             "valor": 21.90, "parcela": None},
            {"data": "2026-10-05", "estabelecimento": "Spotify",
             "valor": 21.90, "parcela": None},
        ]
        assert detectar_duplicidade(lancamentos) == []
```

> Enquanto as funções forem esqueletos, os 3 testes falham com `NotImplementedError` (e não com erro de importação), que é o resultado esperado da Sprint 2.

### Referência rápida para a review cruzada

| Caso | Entrada | Saída esperada |
|------|---------|----------------|
| 2 iguais | 2 × 49.90, mesma data e loja | duplicidade, indevido 49.90 |
| 3 iguais | 3 × 49.90, mesma data e loja | duplicidade, indevido 99.80 |
| Loja com caixa/espaço diferente | `"Netflix"` vs `"  NETFLIX "` | tratados como o mesmo estabelecimento |
| Mensalidade | mesmo valor e loja, datas diferentes | sem duplicidade |
| `13/12` | N > M | inconsistente: parcela maior que o total |
| `0/12` | N < 1 | inconsistente: parcela menor que 1 |
| `3-12`, `abc` | formato fora de N/M | inconsistente: formato inválido |
| `3/12` | válida | não aponta |

### Mensagem de commit sugerida

```
Adiciona esqueletos e testes da História 2 (detectar suspeitas)
```

### Lembretes de convivência

- `git pull` antes de cada `git push`.
- Mexer só na classe `TestHU2` e na seção da História 2.
- Ler os critérios das Histórias 1 e 3 para conseguir explicar qualquer decisão na review.
