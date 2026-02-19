"""
Ambiguity Analyzer V2
Responsável por decidir se o agente pode prosseguir
ou se a pergunta é ambígua / incompleta.

- NÃO gera SQL
- NÃO interpreta linguagem natural
- NÃO cria regra
- NÃO executa correção automática

Ele apenas DECIDE o ESTADO do pipeline.
"""

from agent_state import AgentState


class AmbiguityAnalyzer:
    def __init__(self, semantic_dictionary):
        self.semantic_dictionary = semantic_dictionary

    def run(self, context):
        intent = context.data.get("intent", {})
        semantic = context.data.get("semantic_resolution", {})
        warnings = context.data.get("rule_warnings", [])
        
        # Debug logging
        print(f"DEBUG: question='{intent.get('raw_question')}' metrics={semantic.get('metrics')} states={semantic.get('states')} flags={intent.get('risk_flags')}")

        blockers = []
        assumptions = []  # NOVO: Documentar suposições para o MODO AGRESSIVO
        
        resolved_metrics = semantic.get("metrics", [])
        resolved_entities = semantic.get("entities", [])
        resolved_states = semantic.get("states", [])
        invalid = semantic.get("invalid_concepts", [])

        # =========================
        # BLOQUEIOS CRÍTICOS (FAIL)
        # =========================
        
        # 1. Conceitos inválidos (não existem no dicionário)
        if invalid:
            context.state = AgentState.FAIL
            context.errors.append(f"Conceitos não reconhecidos: {', '.join(invalid)}")
            return context
        
        # 2. Entidades incompatíveis (Venda + Pagar)
        if "venda" in resolved_entities and "pagar" in resolved_entities:
            context.state = AgentState.FAIL
            context.errors.append("Consulta envolve entidades incompatíveis (Venda x Pagar)")
            return context
        
        # 3. Nenhum conceito reconhecido
        if not resolved_metrics and not resolved_entities:
            context.state = AgentState.FAIL
            context.errors.append("Nenhum conceito de negócio reconhecido ou compatível")
            return context

        # =========================
        # SUPOSIÇÕES INTELIGENTES (PARTIAL)
        # =========================
        
        # 4. Agregação sem métrica explícita → Assume COUNT
        if intent.get("type") == "aggregation" and not resolved_metrics:
            assumptions.append("Métrica não especificada - assumindo contagem (COUNT)")
        
        # 5. Sem período temporal → Assume "todo o histórico" ou "hoje" conforme entidade
        time_refs = semantic.get("time_refs", [])
        if not time_refs:
            if "venda" in resolved_entities or "faturamento" in resolved_metrics:
                assumptions.append("Período não especificado - considerando últimos 30 dias")
            elif "os" in resolved_entities:
                assumptions.append("Período não especificado - considerando todo o histórico de Ordens de Serviço")
            else:
                assumptions.append("Período não especificado - considerando todo o histórico")

        # 6. Sem estado para vendas → Assume "concluídas"
        if ("venda" in resolved_entities or "faturamento" in resolved_metrics) and not resolved_states:
            assumptions.append("Estado não especificado - considerando apenas vendas concluídas (STATUS='F')")
            semantic["states"].append("venda_concluida")
            
        # 7. Títulos financeiros sem estado → Assume "em aberto"
        # Se 'excluido' está nos estados, NÃO força 'em_aberto'
        if ("pagar" in resolved_entities or "receber" in resolved_entities) and not resolved_states:
            if "excluido" not in resolved_states:
                assumptions.append("Estado não especificado - considerando apenas títulos em aberto (A)")
                semantic["states"].append("em_aberto")
        
        # 8. Auditoria sem alvo específico → Assume contexto atual
        if "usuario" in resolved_entities and not resolved_metrics:
            assumptions.append("Consulta de auditoria - listando últimos eventos por usuário")

        # =========================
        # DECISÃO FINAL
        # =========================
        
        # Se temos suposições, retorna PARTIAL (gera SQL com avisos)
        if assumptions:
            context.state = AgentState.PARTIAL
            context.data["assumptions"] = assumptions
            print(f"[PARTIAL] Assumptions: {assumptions}")
            return context
        
        # Caso contrário, tudo OK
        context.state = AgentState.OK
        return context
        return context
