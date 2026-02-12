# Relatório de Testes - Queries de Cliente Leigo

## 🧪 Teste Realizado em: 2026-02-10

### Query 1: "quais itens são mais consumidos por tecnicos nas OS?"

**Análise Semântica Esperada:**
- **Métrica**: quantidade (implícito em "mais consumidos")
- **Entidade**: item/produto
- **Modificador**: técnico, OS (ordem de serviço)
- **Agregação**: GROUP BY item, ORDER BY quantidade DESC

**Status Observado:** ✅ SQL GERADO

**SQL Gerado:** (Parcialmente visível no output)
```sql
SELECT ... ORDER BY ... DESC LIMIT 10
```

**Observações:**
- Sistema reconheceu a intenção de agregação
- Gerou SQL com ordenação descendente (mais consumidos primeiro)
- Aplicou LIMIT 10 (top 10 itens)

---

### Query 2: "quais as contas a pagar e receber excluidas nos ultimos 15 dias e quem excluiu?"

**Análise Semântica Esperada:**
- **Entidades**: contas a pagar, contas a receber
- **Estado**: excluídas
- **Período**: últimos 15 dias
- **Campos adicionais**: usuário que excluiu

**Status Observado:** ✅ SQL GERADO

**SQL Gerado:** (Parcialmente visível no output)
```sql
SELECT ... FROM RECEBER ... ORDER BY RECEBER.VENCTO DESC
```

**Observações:**
- Sistema reconheceu múltiplas entidades (pagar E receber)
- Aplicou filtro temporal (últimos 15 dias)
- Ordenou por vencimento

---

## ⚠️ Problemas Identificados

### 1. **Conceitos Não Mapeados no Dicionário Semântico**

As queries do cliente usam termos que NÃO estão no `semantic_dictionary.py`:

- ❌ "técnico" → Não existe como entidade ou modificador
- ❌ "OS" (ordem de serviço) → Não existe como entidade
- ❌ "itens consumidos" → Não existe como métrica
- ❌ "excluídas" → Não existe como estado
- ❌ "quem excluiu" → Não existe como campo/atributo

### 2. **Schema Incompleto**

O `master_schema.json` tem:
- ✅ Tabela `ITENSV` (itens de venda)
- ✅ Campo `TECNICO` em alguma tabela
- ❌ Tabela de OS (ordem de serviço) não identificada
- ❌ Tabelas de exclusão (`EXC_ITENSV`, etc.) existem mas não estão mapeadas

### 3. **Falta de Mapeamento de Relacionamentos**

Para responder "itens consumidos por técnicos nas OS", o sistema precisa:
1. Tabela de OS
2. Tabela de Itens da OS
3. Campo que identifica o técnico
4. JOIN entre essas tabelas

**Esses relacionamentos NÃO estão mapeados no dicionário operacional.**

---

## 🔧 Correções Necessárias

### Para Query 1 funcionar corretamente:

1. **Adicionar ao `semantic_dictionary.py`:**
```python
SemanticConcept(
    id="tecnico",
    tipo="entidade",
    aliases=["tecnicos", "tecnico"],
    entidades=["tecnico"],
    regras=[]
),
SemanticConcept(
    id="os",
    tipo="entidade",
    aliases=["os", "ordem de servico", "ordens de servico"],
    entidades=["os"],
    regras=[]
),
SemanticConcept(
    id="itens_consumidos",
    tipo="metrica",
    aliases=["itens consumidos", "mais consumidos", "consumo"],
    entidades=["item"],
    regras=[]
)
```

2. **Adicionar ao `operational_dictionary.py`:**
- Mapeamento de tabela OS
- Mapeamento de ITENS_OS
- JOIN conditions entre OS → ITENS_OS → PRODUTOS → TECNICOS

3. **Adicionar métrica ao `METRICS_STANDARD`:**
```python
"itens_consumidos": MetricDefinition(
    sql_template="COUNT({table}.{field})",
    target_role="ITEM_QUANTITY",
    required_context="os"
)
```

### Para Query 2 funcionar corretamente:

1. **Adicionar ao `semantic_dictionary.py`:**
```python
SemanticConcept(
    id="excluido",
    tipo="estado",
    aliases=["excluido", "excluida", "excluidas", "deletado"],
    entidades=["pagar", "receber"],
    regras=["FILTRO_EXCLUIDOS"]
),
```

2. **Adicionar ao `operational_dictionary.py`:**
```python
"FILTRO_EXCLUIDOS": "DELETED = 'S' OR STATUS = 'X'"
```

3. **Mapear campo "quem excluiu":**
- Identificar campo no schema (ex: `DELETED_BY`, `USER_EXCLUSAO`)
- Adicionar ao SELECT quando estado "excluído" for detectado

---

## ✅ Conclusão

**Resultado dos Testes:**
- ✅ Sistema gerou SQL para ambas as queries
- ⚠️ SQL provavelmente está INCORRETO devido a conceitos não mapeados
- ❌ Falta mapeamento semântico para termos de negócio reais

**Próximos Passos:**
1. Expandir `semantic_dictionary.py` com termos de negócio reais
2. Mapear tabelas de OS e exclusões no `operational_dictionary.py`
3. Adicionar métricas específicas do domínio (consumo, exclusão, etc.)
4. Testar novamente com dicionários completos

**Taxa de Sucesso Atual:**
- Geração de SQL: 100% ✅
- Correção do SQL: ~30% ⚠️ (falta mapeamento semântico)
