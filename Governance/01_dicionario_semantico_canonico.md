# Dicionário Semântico Canônico do Agente ERP

## Objetivo
Este documento é a **única fonte de verdade semântica** do agente analista de banco de dados.

Ele define **conceitos de negócio**, **entidades**, **métricas**, **estados** e **restrições**, **sem qualquer referência a SQL, banco de dados ou tecnologia**.

Todo código deve **consumir** este dicionário — nunca interpretá-lo ou alterá-lo.

---

## Princípios Fundamentais (Regras-Mãe)

1. Nenhum conceito de negócio conhece SQL
2. Nenhum conceito conhece nomes de tabelas ou campos
3. Detecção linguística **não decide** — apenas sugere
4. Ambiguidade é um estado válido
5. SQL só nasce na última etapa do pipeline

---

## Estrutura do Dicionário

Cada entrada semântica segue o formato:

```
CONCEITO:
  tipo:
  descricao:
  entidades:
  regras:
  observacoes:
```

---

## 1. Estados de Negócio

### venda_concluida
- tipo: estado_negocio
- descricao: Venda finalizada e autorizada fiscalmente
- entidades: [venda]
- regras:
  - exige_documento_fiscal
  - exclui_cancelamentos
- observacoes:
  - Pode existir sem recebimento financeiro

---

### venda_cancelada
- tipo: estado_negocio
- descricao: Venda invalidada após emissão ou tentativa de emissão
- entidades: [venda]
- regras:
  - invalida_faturamento
  - invalida_ticket_medio
- observacoes:
  - Não deve compor indicadores financeiros

---

### titulo_baixado
- tipo: estado_financeiro
- descricao: Título financeiro quitado
- entidades: [titulo_receber, titulo_pagar]
- regras:
  - encerra_obrigacao
- observacoes:
  - Baixa parcial deve ser tratada explicitamente

---

## 2. Entidades de Negócio

### venda
- tipo: entidade
- descricao: Operação comercial de venda
- relacionamentos:
  - possui_itens -> item_venda
  - gera -> titulo_receber

---

### item_venda
- tipo: entidade
- descricao: Produto ou serviço vinculado a uma venda
- observacoes:
  - Pode existir sem impacto financeiro direto

---

### cliente
- tipo: entidade
- descricao: Pessoa física ou jurídica compradora

---

## 3. Métricas de Negócio

### faturamento
- tipo: metrica
- descricao: Soma do valor das vendas válidas
- depende_de: [venda_concluida]
- restricoes:
  - exclui_vendas_canceladas

---

### ticket_medio
- tipo: metrica
- descricao: Valor médio por venda válida
- composicao:
  - numerador: faturamento
  - denominador: quantidade_vendas
- restricoes:
  - somente_vendas_validas

---

### inadimplencia
- tipo: indicador
- descricao: Títulos vencidos e não quitados
- entidades: [titulo_receber]
- restricoes:
  - vencimento_passado
  - nao_baixado

---

## 4. Períodos Temporais (Conceituais)

### mes_atual
- tipo: periodo
- descricao: Intervalo correspondente ao mês corrente
- observacoes:
  - Deve respeitar o calendário fiscal

---

### mes_anterior
- tipo: periodo
- descricao: Intervalo correspondente ao mês imediatamente anterior

---

### ultimos_30_dias
- tipo: periodo
- descricao: Janela móvel de 30 dias retroativos

---

## 5. Formas de Pagamento (Conceituais)

### pix
- tipo: meio_pagamento
- descricao: Transferência instantânea via PIX

---

### cartao_credito
- tipo: meio_pagamento
- descricao: Pagamento via cartão de crédito

---

### dinheiro
- tipo: meio_pagamento
- descricao: Pagamento em espécie

---

## 6. Ambiguidades Conhecidas

### vendas_do_mes
- tipo: ambiguidade
- descricao: Não define se considera vendas canceladas ou não
- requer:
  - esclarecimento_estado

---

## 7. Estados de Resposta do Agente

- OK: resposta completa e confiável
- PARTIAL: resposta possível com ressalvas
- AMBIGUOUS: múltiplas interpretações válidas
- FAIL: impossível responder com segurança

---

## Encerramento

Este dicionário **não executa**, **não infere** e **não corrige**.

Ele apenas **define significado**.

Todo comportamento do agente deve emergir do **pipeline**, nunca deste arquivo.

