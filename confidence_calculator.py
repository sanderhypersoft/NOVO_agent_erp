from agent_state import AgentState

class ConfidenceCalculator:
    def __init__(self, semantic_dictionary):
        self.semantic_dictionary = semantic_dictionary
    def run(self, context):
        score = 0

        if context.state in [AgentState.OK, AgentState.PARTIAL]:
            score = 90
        elif context.state == AgentState.AMBIGUOUS:
            score = 30
        else:
            score = 0

        context.score = score
        return context
