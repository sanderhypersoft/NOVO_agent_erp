# Score de Confiança e Critérios de Resposta do Agente

## Objetivo
Definir **como o agente mede a confiabilidade de uma resposta** e **quando deve responder ou se abster**.

Este documento impede respostas "bonitas e erradas".

---

## Princípios

1. Confiança é calculada, não estimada
2. Fluidez textual não aumenta confiança
3. Ambiguidade reduz confiança
4. Violação do pipeline invalida resposta

---

## Estados de Resposta (Obrigatórios)

| Estado | Significado | Pode gerar SQL |
|------|------------|---------------|
| OK | Resposta completa e inequívoca | Sim |
| PARTIAL | Resposta possível com ressalvas | Sim (com aviso) |
| AMBIGUOUS | Múltiplas interpretações válidas | Não |
| FAIL | Impossível responder com segurança | Não |

---

## Componentes do Score de Confiança

O score final varia de **0 a 100** e é composto por critérios objetivos.

### 1. Pipeline Completo (0–40 pontos)

| Condição | Pontos |
|--------|--------|
| Todas as etapas concluídas | 40 |
| 1 etapa com ressalva | 25 |
| Etapa crítica falhou | 0 |

---

### 2. Ambiguidade (0–30 pontos)

| Situação | Pontos |
|--------|--------|
| Nenhuma ambiguidade | 30 |
| Ambiguidade resolvida implicitamente | 15 |
| Ambiguidade não resolvida | 0 |

---

### 3. Regras de Negócio Aplicadas (0–20 pontos)

| Situação | Pontos |
|--------|--------|
| Todas as regras necessárias aplicadas | 20 |
| Regras aplicadas parcialmente | 10 |
| Regra ignorada | 0 |

---

### 4. Aderência ao Mapeamento Técnico (0–10 pontos)

| Situação | Pontos |
|--------|--------|
| Uso correto de entidades e campos | 10 |
| Uso parcial | 5 |
| Violação | 0 |

---

## Interpretação do Score

| Score | Ação do Agente |
|------|---------------|
| 90–100 | Responder normalmente |
| 70–89 | Responder com aviso |
| 50–69 | PARTIAL obrigatório |
| 30–49 | AMBIGUOUS obrigatório |
| < 30 | FAIL obrigatório |

---

## Regras de Bloqueio Absoluto

Independentemente do score, o agente **NÃO PODE responder** se:

- Pipeline foi violado
- Entidade inexistente
- Métrica sem definição
- JOIN não declarado

Nesses casos, o estado é automaticamente **FAIL**.

---

## Transparência da Resposta

Sempre que possível, a resposta deve incluir:

- estado da resposta
- score de confiança
- regras aplicadas
- ressalvas (se houver)

---

## Encerramento

Este documento é **obrigatório** para:
- testes
- validação
- produção

Qualquer resposta fora destes critérios é considerada **defeito grave do agente**.
