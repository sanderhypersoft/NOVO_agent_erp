from supabase_adapter import SupabaseAdapter
from agent_state import AgentState

class IntelligenceLogger:
    def __init__(self):
        self.adapter = SupabaseAdapter()

    def log(self, context):
        """
        Logs the query, generated SQL, and result status to Supabase.
        """
        payload = {
            "question": context.data.get("question", "Unknown"),
            "generated_sql": context.data.get("sql"),
            "error_message": "; ".join(context.errors) if context.errors else None,
            "execution_status": "SUCCESS" if context.state == AgentState.OK else "ERROR",
            "confidence_score": context.data.get("confidence", 0.0)
        }
        try:
            self.adapter.log_intelligence(payload)
            print("DEBUG: Inteligência registrada no Supabase.")
        except Exception as e:
            print(f"Warning: Falha ao registrar log de inteligência ({e})")
