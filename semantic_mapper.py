"""
Semantic Mapper V2
Responsável por cruzar o IntentExtractor com o
Dicionário Semântico Canônico.

- NÃO cria conceitos
- NÃO interpreta SQL
- NÃO resolve ambiguidade
- NÃO aplica regra de negócio

Apenas valida e estrutura conceitos SEMÂNTICOS.
"""
from agent_state import AgentState


class SemanticMapper:

    def __init__(self, semantic_dictionary):
        self.dictionary = semantic_dictionary

    def run(self, context):
        intent = context.data.get("intent")

        if not intent:
            context.state = AgentState.FAIL
            context.errors.append("Intent ausente no contexto")
            return context

        resolved = {
            "metrics": [],
            "entities": [],
            "states": [],
            "time_refs": [],
            "modifiers": [],
            "invalid_concepts": [],
        }

        # =========================
        # MÉTRICAS
        # =========================
        for metric in intent.get("metric_candidates", []):
            if self.dictionary.has_metric(metric):
                resolved["metrics"].append(metric)
            else:
                resolved["invalid_concepts"].append(metric)

        # =========================
        # ENTIDADES
        # =========================
        for entity in intent.get("entity_candidates", []):
            if self.dictionary.has_entity(entity):
                resolved["entities"].append(entity)
            else:
                resolved["invalid_concepts"].append(entity)

        # =========================
        # ESTADOS
        # =========================
        for state in intent.get("state_candidates", []):
            if self.dictionary.has_state(state):
                resolved["states"].append(state)
            else:
                resolved["invalid_concepts"].append(state)

        # =========================
        # TEMPO
        # =========================
        for time_ref in intent.get("time_candidates", []):
            label = time_ref["label"] if isinstance(time_ref, dict) else time_ref
            if self.dictionary.has_time_reference(label):
                resolved["time_refs"].append(time_ref)
            else:
                resolved["invalid_concepts"].append(label)

        # =========================
        # MODIFICADORES
        # =========================
        for mod in intent.get("modifier_candidates", []):
            if self.dictionary.has_modifier(mod):
                resolved["modifiers"].append(mod)
            else:
                resolved["invalid_concepts"].append(mod)

        # Passar o tipo de intenção
        resolved["intent_type"] = intent.get("type", "detail")
        
        context.data["semantic_resolution"] = resolved

        # =========================
        # ESTADO DO PIPELINE
        # =========================
        if resolved["invalid_concepts"]:
            context.state = AgentState.PARTIAL
        else:
            context.state = AgentState.OK

        return context
