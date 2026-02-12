# Mapeamento Completo de Travas do Sistema

## 🎯 Objetivo do Usuário
**"100% de perguntas devem gerar SQL"**
- Se a resposta não for a desejada, o usuário pergunta novamente
- Priorizar AÇÃO sobre VALIDAÇÃO excessiva

---

## 🚫 TRAVAS ATUAIS (O que bloqueia SQL)

### 1. **FAIL - Bloqueio Total** (agent_state.py)
Quando `context.state = AgentState.FAIL`, o SQL **NÃO é gerado**.

#### Causas de FAIL:

**A) ambiguity_analyzer.py - Linha 85-87**
```python
if "venda" in resolved_entities and "pagar" in resolved_entities:
    context.state = AgentState.FAIL
    context.errors.append("Consulta envolve entidades incompatíveis (Venda x Pagar)")
```
**Exemplo bloqueado:** "Faturamento de vendas e contas a pagar"

---

**B) ambiguity_analyzer.py - Linha 90-93**
```python
if intent.get("type") == "aggregation" and not resolved_metrics:
    context.state = AgentState.FAIL
    context.errors.append("Métrica não suportada ou não identificada")
```
**Exemplo bloqueado:** "Quanto foi o total?" (sem métrica clara)

---

**C) ambiguity_analyzer.py - Linha 110-113**
```python
if not resolved_metrics and not semantic.get("entities"):
    context.state = AgentState.FAIL
    context.errors.append("Nenhum conceito de negócio reconhecido ou compatível")
```
**Exemplo bloqueado:** "Mostre os dados" (sem métrica E sem entidade)

---

**D) ambiguity_analyzer.py - Linha 122-125**
```python
if invalid:  # Conceitos não reconhecidos
    context.state = AgentState.FAIL
    context.errors.append(f"Conceitos não reconhecidos: {', '.join(invalid)}")
```
**Exemplo bloqueado:** "Faturamento de xpto" (xpto não existe no dicionário)

---

**E) rule_engine.py - Linha 25-27**
```python
if not semantic:
    context.state = AgentState.FAIL
    context.errors.append("Semantic resolution ausente")
```
**Exemplo bloqueado:** Falha interna no pipeline

---

### 2. **AMBIGUOUS - Pede Esclarecimento** (agent_state.py)
Quando `context.state = AgentState.AMBIGUOUS`, o SQL **NÃO é gerado**.

#### Causas de AMBIGUOUS:

**A) ambiguity_analyzer.py - Linha 48-51 (CORRIGIDO)**
```python
if flag == "SEM_REFERENCIA_TEMPORAL" and not has_temporal_modifier:
    resolved_states = semantic.get("states", [])
    if not resolved_states:
        clarifications.append("Informe o período da consulta")
```
**Exemplo bloqueado:** "Qual o faturamento?" (sem período E sem estado)
**Exemplo liberado:** "Faturamento de vendas concluídas" (tem estado)

---

**B) ambiguity_analyzer.py - Linha 58-63 (CORRIGIDO)**
```python
if warn == "VENDA_SEM_PERIODO":
    resolved_states = semantic.get("states", [])
    if not resolved_states:
        clarifications.append("Vendas exigem um período ou estado definido")
```
**Exemplo bloqueado:** "Faturamento" (sem período E sem estado)
**Exemplo liberado:** "Faturamento de vendas concluídas" (tem estado)

---

**C) ambiguity_analyzer.py - Linha 115-129**
```python
if clarifications:
    # Exceção para ticket_medio e performance
    if "ticket_medio" in resolved_metrics or "performance" in resolved_metrics:
        context.state = AgentState.PARTIAL  # Prossegue
    else:
        context.state = AgentState.AMBIGUOUS  # Bloqueia
```
**Exemplo bloqueado:** Qualquer query que gere `clarifications` (exceto ticket_medio/performance)

---

**D) rule_engine.py - Linha 57-59**
```python
if not entities and metrics:
    warnings.append("METRICA_SEM_ENTIDADE")
    context.state = AgentState.AMBIGUOUS
```
**Exemplo bloqueado:** "Qual o faturamento?" (métrica sem entidade inferida)

---

**E) rule_engine.py - Linha 82-84**
```python
if "baixado" in states and "em_aberto" in states:
    warnings.append("ESTADOS_CONFLITANTES")
    context.state = AgentState.AMBIGUOUS
```
**Exemplo bloqueado:** "Títulos baixados e em aberto" (estados conflitantes)

---

### 3. **PARTIAL - SQL Gerado com Avisos**
Quando `context.state = AgentState.PARTIAL`, o SQL **É GERADO** mas com avisos.

**Não bloqueia SQL!** ✅

---

### 4. **OK - SQL Gerado Normalmente**
Quando `context.state = AgentState.OK`, o SQL **É GERADO** sem problemas.

**Não bloqueia SQL!** ✅

---

## 🔧 Recomendações para "100% SQL"

### Estratégia 1: **Modo Agressivo** (Gera SQL sempre)
Transformar todos os `AMBIGUOUS` em `PARTIAL`:

```python
# Em ambiguity_analyzer.py, linha 127
if clarifications:
    context.state = AgentState.PARTIAL  # Ao invés de AMBIGUOUS
    context.data["warnings"] = clarifications  # Avisos ao invés de bloqueio
```

**Vantagens:**
- ✅ 100% de queries geram SQL
- ✅ Usuário vê o resultado e pode refinar

**Desvantagens:**
- ⚠️ Pode gerar SQL incorreto para queries muito ambíguas
- ⚠️ Usuário pode receber dados inesperados

---

### Estratégia 2: **Modo Inferência** (Assume defaults)
Adicionar defaults para queries incompletas:

```python
# Se não tem período E não tem estado, assume:
- Período: "últimos 30 dias"
- Estado: "concluídas" (para vendas)
```

**Vantagens:**
- ✅ Gera SQL com suposições razoáveis
- ✅ Usuário pode refinar se necessário

**Desvantagens:**
- ⚠️ Pode surpreender o usuário com filtros não pedidos

---

### Estratégia 3: **Modo Híbrido** (Recomendado)
- **Queries com conceitos válidos**: Gera SQL com defaults
- **Queries com conceitos inválidos**: Bloqueia (FAIL)

```python
# Exemplo:
"Faturamento" → PARTIAL (assume vendas concluídas dos últimos 30 dias)
"Faturamento de xpto" → FAIL (xpto não existe)
```

---

## 📊 Resumo de Bloqueios Atuais

| Tipo | Condição | Gera SQL? | Arquivo | Linha |
|------|----------|-----------|---------|-------|
| FAIL | Entidades incompatíveis (venda + pagar) | ❌ | ambiguity_analyzer.py | 85-87 |
| FAIL | Agregação sem métrica | ❌ | ambiguity_analyzer.py | 90-93 |
| FAIL | Sem métrica E sem entidade | ❌ | ambiguity_analyzer.py | 110-113 |
| FAIL | Conceitos inválidos | ❌ | ambiguity_analyzer.py | 122-125 |
| AMBIGUOUS | Sem período E sem estado | ❌ | ambiguity_analyzer.py | 48-51, 58-63 |
| AMBIGUOUS | Métrica sem entidade | ❌ | rule_engine.py | 57-59 |
| AMBIGUOUS | Estados conflitantes | ❌ | rule_engine.py | 82-84 |
| PARTIAL | Ticket médio sem período | ✅ | ambiguity_analyzer.py | 117-119 |
| OK | Query completa | ✅ | - | - |

---

## 🎯 Próximos Passos

**Qual estratégia você prefere?**

1. **Agressiva**: Tudo vira PARTIAL, sempre gera SQL
2. **Inferência**: Assume defaults inteligentes (ex: últimos 30 dias)
3. **Híbrida**: Gera SQL quando possível, bloqueia apenas conceitos inválidos

**Recomendo a Estratégia 3 (Híbrida)** para balancear utilidade e precisão.
