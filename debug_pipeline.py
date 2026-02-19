from pipeline_executor import PipelineExecutor
from agent_state import AgentState

executor = PipelineExecutor()
question = "Quantas contas a pagar foram excluidas nos ultimos 30 dias?"
context = executor.run(question)

print(f"--- DEBUG PIPELINE ---")
print(f"Question: {question}")
print(f"Entities: {context.data.get('semantic_resolution', {}).get('entities')}")
print(f"States: {context.data.get('semantic_resolution', {}).get('states')}")
print(f"SQL: {context.data.get('sql')}")
print(f"State: {context.state}")
print(f"Errors: {context.errors}")
