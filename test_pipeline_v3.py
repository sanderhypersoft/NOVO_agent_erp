from pipeline_executor import PipelineExecutor
from agent_state import AgentState

def test_complex_query():
    executor = PipelineExecutor()
    question = "Quantas contas a pagar foram excluidas nos ultimos 30 dias, qual o valor total excluido, e qual usuario realizou mais exclusoes nesse periodo?"
    
    context = executor.run(question)
    
    print(f"Question: {question}")
    print(f"State: {context.state}")
    print(f"Confidence: {context.data.get('confidence', 0)}%")
    
    if context.data.get("sql"):
        print(f"\nGenerated SQL:\n{context.data['sql']}")
    
    if context.errors:
        print(f"\nErrors: {context.errors}")
    
    if context.data.get("steps_results"):
        print(f"\nMulti-Step Results: {len(context.data['steps_results'])}")
        for i, step in enumerate(context.data['steps_results']):
            print(f"Step {i+1} SQL: {step['sql']}")

if __name__ == "__main__":
    test_complex_query()
