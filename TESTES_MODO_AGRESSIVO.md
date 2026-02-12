# Teste de Queries - Modo Agressivo

## ✅ Queries que DEVEM gerar SQL agora:

### 1. Faturamento sem período
**Query:** "Qual o faturamento?"
**Esperado:** 
- Status: PARTIAL
- SQL: `SELECT SUM(VENDAS.TOTAL) AS FATURAMENTO FROM VENDAS WHERE VENDAS.STATUS = 'F'`
- Assumptions:
  - "Estado não especificado - considerando apenas vendas concluídas (STATUS='F')"
  - "Período não especificado - considerando todo o histórico de vendas concluídas"

### 2. Faturamento de vendas concluídas (sem período)
**Query:** "Qual o faturamento de vendas concluídas?"
**Esperado:**
- Status: PARTIAL
- SQL: `SELECT SUM(VENDAS.TOTAL) AS FATURAMENTO FROM VENDAS WHERE VENDAS.STATUS = 'F'`
- Assumptions:
  - "Período não especificado - considerando todo o histórico de vendas concluídas"

### 3. Listagem de clientes
**Query:** "Mostre os clientes"
**Esperado:**
- Status: OK ou PARTIAL
- SQL: `SELECT CLIENTES.CODIGO, CLIENTES.NOME, ... FROM CLIENTES`

### 4. Quanto vendemos (sem período, sem estado)
**Query:** "Quanto vendemos?"
**Esperado:**
- Status: PARTIAL
- SQL: `SELECT SUM(VENDAS.TOTAL) AS FATURAMENTO FROM VENDAS WHERE VENDAS.STATUS = 'F'`
- Assumptions:
  - "Métrica inferida: faturamento"
  - "Estado não especificado - considerando apenas vendas concluídas"
  - "Período não especificado - considerando todo o histórico"

### 5. Estados conflitantes
**Query:** "Títulos baixados e em aberto"
**Esperado:**
- Status: PARTIAL
- SQL: `SELECT ... FROM RECEBER WHERE (STATUS = 'B' OR STATUS = 'A')`
- Assumptions:
  - "Estados conflitantes detectados - considerando títulos baixados OU em aberto"

---

## ❌ Queries que DEVEM FALHAR:

### 1. Conceitos inválidos
**Query:** "Faturamento de xpto"
**Esperado:**
- Status: FAIL
- Erro: "Conceitos não reconhecidos: xpto"

### 2. Entidades incompatíveis
**Query:** "Faturamento de vendas e contas a pagar"
**Esperado:**
- Status: FAIL
- Erro: "Consulta envolve entidades incompatíveis (Venda x Pagar)"

### 3. Sem conceitos
**Query:** "Mostre os dados"
**Esperado:**
- Status: FAIL
- Erro: "Nenhum conceito de negócio reconhecido ou compatível"

---

## 🧪 Como Testar

### Postman:
```
POST http://localhost:8000/agent/query
Content-Type: application/json

{
  "question": "Qual o faturamento?"
}
```

### Resposta Esperada:
```json
{
  "status": "PARTIAL",
  "query": "Qual o faturamento?",
  "sql": "SELECT SUM(VENDAS.TOTAL) AS FATURAMENTO FROM VENDAS WHERE VENDAS.STATUS = 'F'",
  "confidence": 75,
  "assumptions": [
    "Estado não especificado - considerando apenas vendas concluídas (STATUS='F')",
    "Período não especificado - considerando todo o histórico de vendas concluídas"
  ],
  "details": { ... }
}
```

---

## 📊 Taxa de Sucesso Esperada

**Antes:** ~60% de queries geravam SQL
**Depois:** ~95% de queries geram SQL

**Bloqueios restantes:** Apenas conceitos inválidos e entidades incompatíveis
