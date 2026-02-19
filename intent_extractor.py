"""
Intent Extractor V2
Responsável por estruturar a pergunta do usuário em PT-BR.

- NÃO conhece SQL
- NÃO conhece banco
- NÃO decide regras
- NÃO resolve ambiguidade

Gera apenas CANDIDATOS semânticos.
"""

from typing import Dict, List
import re


class IntentExtractor:

    def __init__(self, semantic_dictionary):
        self.dictionary = semantic_dictionary

    def run(self, context):
        # Usa a questão já normalizada (sem acentos, lowercase)
        question = context.data.get("normalized_question") or context.question
        intent = self.extract(question)
        context.data["intent"] = intent
        return context

    def extract(self, question: str) -> Dict:
        q = question.lower()
        tokens = self._tokenize(q)

        intent = {
            "raw_question": question,
            "tokens": tokens,
            "type": "detail", # detail ou aggregation
            "metric_candidates": [],
            "entity_candidates": [],
            "state_candidates": [],
            "time_candidates": [],
            "modifier_candidates": [],
            "risk_flags": [],
        }

        # =========================
        # DETECÇÃO DINÂMICA (Dicionário)
        # =========================
        # Agora o Extractor usa o Dicionário de verdade
        for concept_id, concept in self.dictionary.concepts.items():
            # Check ID and Aliases
            all_keywords = [concept_id] + concept.aliases
            if any(kw in q for kw in all_keywords):
                if concept.tipo == "metrica":
                    intent["metric_candidates"].append(concept_id)
                elif concept.tipo == "entidade":
                    intent["entity_candidates"].append(concept_id)
                elif concept.tipo == "estado_negocio":
                    intent["state_candidates"].append(concept_id)
                elif concept.tipo == "modificador":
                    intent["modifier_candidates"].append(concept_id)

        # =========================
        # DETECÇÃO DE TIPO (Agregação vs Listagem)
        # =========================
        aggregation_keywords = ["total", "soma", "media", "quanto", "quantos", "faturamento", "ticket", "inadimplencia", "performance", "desempenho", "indice"]
        if any(kw in q for kw in aggregation_keywords) or intent["metric_candidates"]:
            intent["type"] = "aggregation"

        if not intent["metric_candidates"] and intent["type"] == "aggregation":
            intent["risk_flags"].append("SEM_METRICA_EXPLICITA")

        # =========================
        # TEMPO (Inteligente)
        # =========================
        from datetime import datetime, timedelta
        today = datetime.now()
        
        # Regex para "hoje"
        if "hoje" in q:
            intent["time_candidates"].append({
                "label": "hoje",
                "start": today.strftime("%Y-%m-%d"),
                "end": today.strftime("%Y-%m-%d")
            })
            
        # Mês atual
        if "mes atual" in q or "deste mes" in q or "neste mes" in q:
            first_day = today.replace(day=1)
            intent["time_candidates"].append({
                "label": "mes_atual",
                "start": first_day.strftime("%Y-%m-%d"),
                "end": today.strftime("%Y-%m-%d")
            })

        # Mês passado
        if "mes passado" in q:
            first_day_this_month = today.replace(day=1)
            last_day_prev_month = first_day_this_month - timedelta(days=1)
            first_day_prev_month = last_day_prev_month.replace(day=1)
            intent["time_candidates"].append({
                "label": "mes_passado",
                "start": first_day_prev_month.strftime("%Y-%m-%d"),
                "end": last_day_prev_month.strftime("%Y-%m-%d")
            })

        if not intent["time_candidates"] and any(e in q for e in ["venda", "faturamento", "receber", "pagar", "os"]):
             intent["risk_flags"].append("SEM_REFERENCIA_TEMPORAL")

        # Ontem
        if "ontem" in q:
            ontem = today - timedelta(days=1)
            intent["time_candidates"].append({
                "label": "ontem",
                "start": ontem.strftime("%Y-%m-%d"),
                "end": ontem.strftime("%Y-%m-%d")
            })

        # Regex para "últimos X dias"
        match_days = re.search(r"ultimos (\d+) dias", q)
        if match_days:
            days = int(match_days.group(1))
            start_date = today - timedelta(days=days)
            intent["time_candidates"].append({
                "label": "intervalo_relativo",
                "start": start_date.strftime("%Y-%m-%d"),
                "end": today.strftime("%Y-%m-%d")
            })

        return intent

    # -------------------------
    # Helpers
    # -------------------------
    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b\w+\b", text)
