import unicodedata
from agent_state import AgentState


class Normalizer:
    def run(self, context):
        text = context.data["original_question"].lower()
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

        context.data["normalized_question"] = text
        context.state = AgentState.OK
        return context
