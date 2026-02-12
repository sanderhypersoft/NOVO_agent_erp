# Pipeline Canônico do Agente Analista ERP

## Objetivo
Definir o **fluxo obrigatório de raciocínio** do agente analista de banco de dados.

Nenhuma resposta pode pular etapas.
Nenhum SQL pode ser gerado fora deste pipeline.

---

## Visão Geral do Pipeline

```
Pergunta do Usuário
  ↓
Normalização Linguística
  ↓
Extração de Intenção
  ↓
Mapeamento Semântico (Dicionário)
  ↓
Validação de Entidades
  ↓
Aplicação de Regras de Negócio
  ↓
Análise de Ambiguidade
  ↓
Definição do Tipo de Resposta
  ↓
Geração de SQL (última etapa)
```

---

## 1. Normalização Linguística

### Objetivo
Padronizar a pergunta sem inferir significado.

### Ações permitidas
- lower case
- remoção de acentos
- remoção de pontuação irrelevante

### Proibido
- sinônimos automáticos
- inferência semântica

### Saída
Texto normalizado.

---

## 2. Extração de Intenção

### Objetivo
Identificar **o que o usuário quer**, não como calcular.

### Exemplos de intenção
- consultar_valor
- comparar_periodos
- listar_entidades
- calcular_metrica

### Regras
- Deve haver **exatamente uma intenção principal**
- Mais de uma → AMBIGUOUS

### Saída
Intenção primária.

---

## 3. Mapeamento Semântico

### Objetivo
Associar palavras da pergunta a **conceitos do Dicionário Canônico**.

### Fontes
- 01_DICIONARIO_SEMANTICO_CANONICO.md

### Resultado possível
- conceitos encontrados
- conceitos ausentes
- conceitos conflitantes

### Regra crítica
Conceito detectado ≠ conceito válido

---

## 4. Validação de Entidades

### Objetivo
Confirmar que os conceitos podem coexistir.

### Exemplos
- venda + cliente → válido
- venda + titulo_pagar → inválido

### Falha
- Entidade incompatível → FAIL

---

## 5. Aplicação de Regras de Negócio

### Objetivo
Restringir o escopo com base em regras declaradas no dicionário.

### Exemplos
- venda_concluida → exclui canceladas
- faturamento → exige venda válida

### Proibido
- criar regras novas

---

## 6. Análise de Ambiguidade

### Objetivo
Determinar se a pergunta admite mais de uma interpretação válida.

### Casos
- período não definido
- estado não definido
- métrica composta sem restrição

### Resultado
- Nenhuma ambiguidade → OK
- Ambiguidade resolvível → PARTIAL
- Ambiguidade crítica → AMBIGUOUS

---

## 7. Definição do Tipo de Resposta

### Estados possíveis

| Estado | Descrição |
|------|---------|
| OK | Resposta completa e confiável |
| PARTIAL | Resposta com ressalvas |
| AMBIGUOUS | Requer esclarecimento |
| FAIL | Não é possível responder |

---

## 8. Geração de SQL

### Pré-condições obrigatórias
- Estado = OK ou PARTIAL
- Entidades válidas
- Métrica definida
- Período definido

### Regras
- SQL deve ser explicável
- SQL deve ser determinístico
- Nenhum fallback automático

### Saída
- SQL final
- lista de regras aplicadas
- score de confiança

---

## 9. Score de Confiança

### Baseado em
- etapas concluídas
- ausência de ambiguidade
- número de regras aplicadas

### Proibido
- fluidez textual
- heurística subjetiva

---

## Encerramento

Este pipeline é **obrigatório**.

Se qualquer etapa falhar:
- interrompa
- explique
- **não gere SQL**.

