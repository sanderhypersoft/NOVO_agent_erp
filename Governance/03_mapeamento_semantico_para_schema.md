# Mapeamento Semântico → Schema Físico (Firebird / ERP)

## Objetivo
Este documento define **como conceitos semânticos se conectam à estrutura física do banco de dados**.

Ele é o **único ponto permitido** onde tabelas, campos, joins e regras técnicas são declarados.

Nenhum outro arquivo pode inferir schema.

---

## Princípios

1. Conceitos semânticos nunca conhecem SQL
2. O pipeline consome este mapeamento
3. O gerador de SQL **não decide**, apenas monta
4. Tudo aqui é explícito e auditável

---

## Estrutura do Documento

Cada entidade semântica segue o formato:

```
ENTIDADE_SEMANTICA:
  tabela_principal:
  chave_primaria:
  campos_relevantes:
  relacionamentos:
  filtros_tecnicos:
```

---

## 1. Entidades Semânticas

### venda
- tabela_principal: VENDAS
- chave_primaria: CONTROLE
- campos_relevantes:
  - DATA
  - STATUS
  - TOTAL
  - CLIENTE
  - LOJA
- relacionamentos:
  - item_venda:
      tabela: ITENSV
      chave_origem: CONTROLE
      chave_destino: CTRVENDA
      tipo: 1-N
  - titulo_receber:
      tabela: RECEBER
      chave_origem: CONTROLE
      chave_destino: CTRVENDA
      tipo: 1-N
- filtros_tecnicos:
  - STATUS IS NOT NULL

---

### item_venda
- tabela_principal: ITENSV
- chave_primaria: CONTROLE
- campos_relevantes:
  - PRODUTO
  - QUANTIDADE
  - VALOR

---

### cliente
- tabela_principal: CLIENTES
- chave_primaria: CODIGO
- campos_relevantes:
  - NOME
  - CPF_CNPJ

---

### titulo_receber
- tabela_principal: RECEBER
- chave_primaria: CONTROLE
- campos_relevantes:
  - VALOR
  - VENCTO
  - BAIXA
  - STATUS

---

## 2. Estados Semânticos → Filtros Técnicos

### venda_concluida
- entidade: venda
- filtros:
  - STATUS = 'Autorizado o uso da NF-e'

---

### venda_cancelada
- entidade: venda
- filtros:
  - STATUS LIKE '%Cancel%'

---

### titulo_baixado
- entidade: titulo_receber
- filtros:
  - BAIXA IS NOT NULL

---

## 3. Métricas → Expressões Técnicas

### faturamento
- entidade_base: venda
- campo_valor: TOTAL
- agregacao: SUM
- restricoes:
  - venda_concluida

---

### quantidade_vendas
- entidade_base: venda
- campo_contagem: CONTROLE
- agregacao: COUNT_DISTINCT
- restricoes:
  - venda_concluida

---

### ticket_medio
- composicao:
  - numerador: faturamento
  - denominador: quantidade_vendas

---

## 4. Períodos → Campos de Data

### venda
- campo_data_padrao: DATA

### titulo_receber
- campo_data_padrao: VENCTO

---

## 5. Regras Técnicas Obrigatórias

- JOINs só podem ocorrer se declarados aqui
- Agregações devem respeitar entidade_base
- Campos fora de campos_relevantes são proibidos

---

## Encerramento

Este documento **conecta significado à execução**.

Qualquer alteração no banco:
- exige atualização aqui
- invalida SQL antigo
- mantém o agente previsível.
