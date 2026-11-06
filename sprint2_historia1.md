## História 1 – Validar a fatura

**Responsável:** Iago Leonardo Alves Martins Sitta

**História de usuário**

Como consumidor que confere a fatura, quero ser avisado quando o arquivo CSV não tiver os campos necessários ou tiver linhas inválidas, para saber se posso confiar na conferência.

### Critérios de aceitação e testes

| Critério | Verificação | Teste |
|----------|-------------|-------|
| CA1 | CSV sem coluna obrigatória (data, estabelecimento ou valor): o sistema não processa a fatura e informa o nome da coluna que falta. | `test_hu1_ca1_coluna_obrigatoria_ausente` |
| CA2 | CSV sem a coluna parcela: processa normalmente e informa que a conferência de parcelas não foi feita. | `test_hu1_ca2_sem_coluna_parcela` |
| CA3 | Linha com valor não numérico ou data inválida: o sistema a ignora, informa o número da linha e processa as demais. | `test_hu1_ca3_linha_invalida_ignorada` |

### Relação entre testes e critérios

| Teste | Critério verificado |
|-------|---------------------|
| `test_hu1_ca1_coluna_obrigatoria_ausente` | CA1 |
| `test_hu1_ca2_sem_coluna_parcela` | CA2 |
| `test_hu1_ca3_linha_invalida_ignorada` | CA3 |
