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

Requer Python 3. Não há dependências externas.

```
git clone https://github.com/kamakawa/Conferidor-de-Fatura-de-Cartao.git
cd Conferidor-de-Fatura-de-Cartao
```

Para rodar os testes automatizados:

```
python -m unittest teste_conferidor_fatura -v
```

## Estrutura do repositório

```
Conferidor-de-Fatura-de-Cartao/
├── README.md
├── docs/
│   ├── sprint1_proposta.md
│   ├── sprint1_pesquisa.md
│   └── sprint2_historias.md
├── conferidor_fatura.py
└── teste_conferidor_fatura.py
```

## Documentação

| Documento | Conteúdo |
|---|---|
| `docs/sprint1_proposta.md` | Definição do trio e descrição do sistema |
| `docs/sprint1_pesquisa.md` | Pesquisa que justifica o sistema, com referências e resumo |
| `docs/sprint2_historias.md` | Histórias de usuário e critérios de aceitação |

## Andamento

| Sprint | Entrega | Situação |
|---|---|---|
| 1 | Proposta e pesquisa | Entregue |
| 2 | Histórias de usuário, critérios de aceitação e testes | Em andamento (os testes ainda falham, pois servem de especificação) |
| 3 | Arquitetura e desenvolvimento das histórias | Pendente |
| 4 | Refatoração e padrões de projeto | Pendente |
