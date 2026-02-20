from pipeline_executor import PipelineExecutor
from agent_state import AgentState

executor = PipelineExecutor()
question = "Quais as ultimas contas a pagar que foram excluídas"
context = executor.run(question)

print(f"--- DEBUG PIPELINE ---")
print(f"Question: {question}")
print(f"Entities: {context.data.get('semantic_resolution', {}).get('entities')}")
print(f"States: {context.data.get('semantic_resolution', {}).get('states')}")
print(f"SQL: {context.data.get('sql')}")
print(f"State: {context.state}")
print(f"Warnings: {context.data.get('rule_warnings')}")
print(f"Steps: {len(context.data.get('steps_results', []))}")
for i, step in enumerate(context.data.get("steps_results", [])):
    print(f"  Step {i+1} SQL: {step['sql']}")
    print(f"  Step {i+1} Result Count: {len(step['results'])}")
