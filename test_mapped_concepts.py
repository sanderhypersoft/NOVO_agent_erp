import sys
sys.path.append("c:/Users/HYPERSOFT/Documents/agent_erp_v2")

from pipeline_executor import PipelineExecutor
from semantic_dictionary import get_semantic_dictionary
from operational_dictionary import OperationalDictionary

pipeline = PipelineExecutor(
    semantic_dictionary=get_semantic_dictionary(),
    operational_dictionary=OperationalDictionary()
)

queries = [
    "quais itens são mais consumidos por tecnicos nas OS?",
    "quais as contas a pagar excluidas nos ultimos 15 dias e quem excluiu?"
]

for q in queries:
    print(f"\nQUERY: {q}")
    ctx = pipeline.run(q)
    print(f"Status: {ctx.state.value}")
    print(f"SQL: {ctx.data.get('sql')}")
    print(f"Flags/Assumptions: {ctx.data.get('assumptions', [])}")
    print(f"Semantic Resolution: {ctx.data.get('semantic_resolution', {})}")
    if ctx.errors:
        print(f"Errors: {ctx.errors}")
