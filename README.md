# Conferidor de Fatura de Cartão

Sistema em Python que ajuda pessoas físicas a identificar cobranças suspeitas na fatura do cartão de crédito antes de pagá-la.

Trabalho final da disciplina de Engenharia de Software.

## Equipe

- Eric Naoki Sugauara Kamakawa
- Iago Leonardo Alves Martins Sitta
- Ives Yudy Omura Maruiti

## O problema

Todo mês, muita gente paga a fatura do cartão sem conferir cada lançamento. Cobranças duplicadas ou parcelas com erro podem passar despercebidas. O Conferidor de Fatura de Cartão lê a fatura detalhada em CSV, aponta lançamentos suspeitos e gera um relatório que o usuário pode levar ao banco numa contestação.

O sistema aponta **suspeitas**, não certezas. Quem decide se contesta é o usuário.

## O que o sistema faz

| Etapa | Descrição |
|---|---|
| Leitura e validação | Lê o CSV, confere as colunas obrigatórias e avisa sobre linhas inválidas |
| Detecção | Procura duplicidades e parcelas inconsistentes |
| Relatório | Gera um relatório em texto com o resumo da fatura e as suspeitas encontradas |

## Formato de entrada

Arquivo CSV com os lançamentos da fatura detalhada:

| Coluna | Obrigatória | Formato | Exemplo |
|---|---|---|---|
| `data` | Sim | DD/MM/AAAA | `06/10/2026` |
| `estabelecimento` | Sim | Texto | `Padoca` |
| `valor` | Sim | Número com ponto decimal | `49.90` |
| `parcela` | Não | N/M | `3/12` |

## Saída

Relatório em texto com a quantidade de lançamentos lidos, o valor total da fatura e, para cada suspeita, o tipo, o motivo, o estabelecimento, a data e o valor possivelmente indevido.

## Como executar

Requer Python 3. Não há dependências externas. Os comandos abaixo devem ser executados na pasta raiz do projeto.

```
git clone https://github.com/Iago2047/Conferidor-de-Fatura-de-Cartao.git
cd Conferidor-de-Fatura-de-Cartao
```

Para executar o programa com a fatura de exemplo:

```
python conferidor_fatura.py exemplos/fatura_exemplo.csv
```

Para rodar todos os testes automatizados:

```
python -m unittest discover -s tests -v
```

Para rodar os testes de uma única história (exemplo: história 3):

```
python -m unittest tests.teste_hu3_gerar_relatorio -v
```

## Estrutura do repositório

```
Conferidor-de-Fatura-de-Cartao/
├── README.md
├── conferidor_fatura.py
├── docs/
│   ├── sprint1/
│   │   └── proposta.pdf
│   └── sprint2/
│       ├── historia1_validar_fatura.md
│       ├── historia2_detectar_suspeitas.md
│       └── historia3_gerar_relatorio.md
├── exemplos/
│   └── fatura_exemplo.csv
└── tests/
    └── teste_hu3_gerar_relatorio.py
```

## Documentação

| Documento | Conteúdo |
|---|---|
| `docs/sprint1/proposta.pdf` | Definição do trio, descrição do sistema e pesquisa com referências e resumo |
| `docs/sprint2/historia1_validar_fatura.md` | História 1 (validar a fatura) e critérios de aceitação |
| `docs/sprint2/historia2_detectar_suspeitas.md` | História 2 (detectar suspeitas) e critérios de aceitação |
| `docs/sprint2/historia3_gerar_relatorio.md` | História 3 (gerar o relatório) e critérios de aceitação |

## Andamento

| Sprint | Entrega | Situação |
|---|---|---|
| 1 | Proposta e pesquisa | Entregue |
| 2 | Histórias de usuário, critérios de aceitação e testes | Em andamento (os testes ainda falham, pois servem de especificação) |
| 3 | Arquitetura e desenvolvimento das histórias | Pendente |
| 4 | Refatoração e padrões de projeto | Pendente |
