from pipeline_executor import PipelineExecutor
from agent_state import AgentState

executor = PipelineExecutor()
question = "Quais as ultimas contas a pagar que foram excluídas"
context = executor.run(question)

print("--- FINAL DATA ---")
print("SQL:", context.data.get("sql"))
print("State:", context.state)
print("Errors:", context.errors)
print("Warnings:", context.data.get("rule_warnings"))
print("Entities:", context.data.get("semantic_resolution", {}).get("entities"))
print("Unique Tables (logged by SQLBuilder should be above)")
