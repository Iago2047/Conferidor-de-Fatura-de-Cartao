## História 3: Gerar o relatório

**Responsável:** Eric Naoki Sugauara Kamakawa

Como consumidor que confere a fatura do cartão, quero receber um relatório em texto com o resumo da fatura e a lista de suspeitas, para analisar e, se achar suspeito, levar ao banco numa contestação

### Dados de exemplo (usados nos critérios)

| Data | Estabelecimento | Valor | Parcela |
|---|---|---|---|
| 06/10/2026 | Padoca | 49.90 | |
| 06/10/2026 | Padoca | 49.90 | |
| 15/10/2026 | Loja Todo Poderoso Timão | 120.00 | 13/12 |
| 20/10/2026 | Mercado Casa das Primas | 230.10 | |

Com esses dados, o sistema lê 4 lançamentos, o total é R$ 449,90 e há 2 suspeitas: duplicidade da Padoca (R$ 49,90 possivelmente indevidos) e parcela inconsistente da Loja Todo Poderoso Timão (R$ 120,00)

### Critérios de aceitação

| Critério | Dado | Quando | Então |
|---|---|---|---|
| **CA1** | Os 4 lançamentos do exemplo | O relatório é gerado | O texto contém a quantidade de lançamentos lidos, no caso 4 e o valor total da fatura que nesse caso é R$ 449,90 |
| **CA2** | As 2 suspeitas do exemplo | O relatório é gerado | Cada suspeita aparece com tipo, motivo, estabelecimento, data e valor possivelmente indevido (exemplo: "Duplicidade", "Padoca", "06/10/2026", "R$ 49,90") |
| **CA3** | Os mesmos lançamentos, sem nenhuma suspeita | O relatório é gerado | O texto informa explicitamente que nenhuma suspeita foi encontrada, e não traz a seção de suspeitas vazia |

### Relação entre testes e critérios

| Teste | Critério verificado |
|---|---|
| `test_hu3_ca1_resumo_da_fatura` | CA1 |
| `test_hu3_ca2_detalhes_da_suspeita` | CA2 |
| `test_hu3_ca3_nenhuma_suspeita` | CA3 |

### Decisões de projeto desta história

| Decisão | Justificativa |
|---|---|
| Relatório em texto | É simples de ler e de verificar |
| Valores no formato brasileiro R$ 449,90 | O usuário é brasileiro e leva o relatório ao banco. Internamente usamos `Decimal` |
| O teste usa `assertIn` e não compara o texto inteiro | Evita que o teste quebre por mudança de espaçamento e verifica o que importa: os dados corretos aparecem |
| Existe um critério para o caso sem suspeitas (CA3) | É um caso comum, e o usuário precisa saber que a conferência rodou e não achou nada |
| Nenhum critério trata de layout | Não há interface gráfica, e critério vago não é verificável |
