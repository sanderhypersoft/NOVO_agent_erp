"""
Rule Engine V2 - AGGRESSIVE MODE
Aplica regras declarativas sobre o resultado semântico.

FILOSOFIA: "Inferir ao invés de bloquear"
- Infere entidades a partir de métricas
- Documenta warnings mas NÃO bloqueia
- Deixa decisão de bloqueio para ambiguity_analyzer
"""
from agent_state import AgentState


class RuleEngine:

    def __init__(self, semantic_dictionary, governance=None):
        self.semantic_dictionary = semantic_dictionary
        self.governance = governance or {}

    def run(self, context):
        semantic = context.data.get("semantic_resolution")

        if not semantic:
            context.state = AgentState.FAIL
            context.errors.append("Semantic resolution ausente")
            return context

        rules_applied = []
        warnings = []

        metrics = semantic.get("metrics", [])
        entities = semantic.get("entities", [])
        states = semantic.get("states", [])
        modifiers = semantic.get("modifiers", [])
        time_refs = semantic.get("time_refs", [])

        # =========================
        # REGRA 1 — Métrica exige entidade (ou infere)
        # =========================
        inferred = []
        if metrics:
            for m in metrics:
                concept = self.semantic_dictionary.get(m)
                if concept and concept.entidades:
                    # Se as entidades exigidas pela métrica não estão presentes, adicione-as
                    for req_ent in concept.entidades:
                        if req_ent not in entities:
                            inferred.append(req_ent)
            
            if inferred:
                unique_inferred = list(set(inferred))
                semantic["entities"].extend(unique_inferred)
                entities = semantic["entities"] # Atualiza local
                rules_applied.append(f"INFERIR_ENTIDADES_{unique_inferred}")

        # MUDANÇA: Não bloqueia mais, apenas documenta
        if not entities and metrics:
            warnings.append("METRICA_SEM_ENTIDADE")
            # NÃO seta context.state = AgentState.AMBIGUOUS

        # =========================
        # REGRA 2 — Entidade venda exige período (Apenas informativo)
        # =========================
        if ("venda" in entities or "faturamento" in metrics) and not time_refs:
            warnings.append("VENDA_SEM_PERIODO")
            # NÃO bloqueia - ambiguity_analyzer vai assumir default
        
        if "inadimplencia" in metrics:
            # Inadimplência é intrinsecamente "atual" se não houver período.
            if not time_refs:
                rules_applied.append("ASSUMIR_DATA_HOJE_PARA_INADIMPLENCIA")

        # =========================
        # REGRA 3 — PIX implica meio de pagamento
        # =========================
        if "pix" in modifiers:
            rules_applied.append("FILTRO_MEIO_PAGAMENTO_PIX")

        # =========================
        # REGRA 4 — Estado baixado não pode coexistir com em_aberto
        # =========================
        if "baixado" in states and "em_aberto" in states:
            warnings.append("ESTADOS_CONFLITANTES")
            # NÃO bloqueia - ambiguity_analyzer vai assumir OR

        # =========================
        # REGRA 5 — Ticket médio exige métrica base
        # =========================
        if "ticket_medio" in metrics and "quantidade" not in metrics:
            rules_applied.append("INFERIR_QUANTIDADE_PARA_TICKET_MEDIO")

        # =========================
        # Persistência no contexto
        # =========================
        context.data["rules_applied"] = rules_applied
        context.data["rule_warnings"] = warnings

        # MUDANÇA: Sempre retorna OK, deixa ambiguity_analyzer decidir
        if context.state not in [AgentState.FAIL]:
            context.state = AgentState.OK

        return context
