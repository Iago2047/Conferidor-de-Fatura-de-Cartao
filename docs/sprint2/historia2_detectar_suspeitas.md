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

- **Chave de duplicidade:** data + estabelecimento normalizado + valor. A normalização remove espaços nas pontas, colapsa espaços internos e ignora maiúsculas/minúsculas.
- **Valor possivelmente indevido:** valor × (repetições − 1). Exemplos: 2 × 49.90 → 49.90; 3 × 49.90 → 99.80.
- **Assinatura mensal não é duplicidade:** a data faz parte da chave, então mesmo estabelecimento e valor em datas diferentes não são agrupados (CA3).
- **Parcela válida:** texto no formato N/M, com N e M inteiros, N ≥ 1 e N ≤ M. Qualquer outra coisa é inconsistente.
- **Lançamento sem parcela** é compra à vista, então não é analisado.
- **Motivos possíveis** da parcela inconsistente: formato inválido, parcela menor que 1, parcela maior que o total.
- **Retorno:** lista vazia quando não há suspeita, para a interface/relatório decidir como exibir.

### Contrato das funções

| Função | Entrada | Saída |
|--------|---------|-------|
| `detectar_duplicidade` | Lista de lançamentos (data, estabelecimento, valor, parcela) | Lista de duplicidades, cada uma com estabelecimento, data, valor, número de repetições e valor possivelmente indevido |
| `detectar_parcela_inconsistente` | Lista de lançamentos (data, estabelecimento, valor, parcela) | Lista de parcelas inconsistentes, cada uma com estabelecimento, parcela, valor do lançamento e motivo |

Neste estágio da Sprint 2, as duas funções são só esqueletos: ao serem chamadas, lançam `NotImplementedError` com uma mensagem indicando o critério (CA1/CA3 para duplicidade, CA2 para parcela).

> Ajustar os nomes dos campos se o modelo de lançamento da Sprint 1 for diferente.

### Testes da classe TestHU2

| Teste | Cenário | O que é verificado |
|-------|---------|--------------------|
| `test_hu2_ca1_duplicidade_detectada` | Dois lançamentos de 49.90 na mesma data; um com "Netflix" e outro com "  NETFLIX " | Uma duplicidade apontada, com 2 repetições e valor indevido de 49.90 |
| `test_hu2_ca2_parcela_invalida_detectada` | Um lançamento com parcela 13/12 e outro com parcela 3/10 | Só o 13/12 é apontado, com o valor do lançamento e um motivo preenchido |
| `test_hu2_ca3_datas_diferentes_nao_e_duplicidade` | Mesmo estabelecimento e valor em meses diferentes | Nenhuma duplicidade apontada |

Enquanto as funções forem esqueletos, os 3 testes falham com `NotImplementedError` (e não com erro de importação), que é o resultado esperado da Sprint 2.

### Referência rápida para a review cruzada

| Caso | Entrada | Resultado esperado |
|------|---------|--------------------|
| 2 iguais | 2 × 49.90, mesma data e loja | Duplicidade, indevido 49.90 |
| 3 iguais | 3 × 49.90, mesma data e loja | Duplicidade, indevido 99.80 |
| Loja com caixa/espaço diferente | "Netflix" vs "  NETFLIX " | Mesmo estabelecimento |
| Mensalidade | Mesmo valor e loja, datas diferentes | Sem duplicidade |
| 13/12 | N maior que M | Inconsistente: parcela maior que o total |
| 0/12 | N menor que 1 | Inconsistente: parcela menor que 1 |
| 3-12, abc | Formato fora de N/M | Inconsistente: formato inválido |
| 3/12 | Válida | Não aponta |

### Commit

Mensagem sugerida: **Adiciona esqueletos e testes da História 2 (detectar suspeitas)**

### Lembretes de convivência

- Rodar `git pull` antes de cada `git push`.
- Mexer só na classe `TestHU2` e na seção da História 2.
- Ler os critérios das Histórias 1 e 3 para conseguir explicar qualquer decisão na review.
