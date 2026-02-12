import sys
sys.path.append("c:/Users/HYPERSOFT/Documents/agent_erp_v2")

from pipeline_executor import PipelineExecutor
from semantic_dictionary import get_semantic_dictionary
from operational_dictionary import OperationalDictionary

pipeline = PipelineExecutor(
    semantic_dictionary=get_semantic_dictionary(),
    operational_dictionary=OperationalDictionary()
)

query = "quais itens sao mais consumidos por tecnicos nas OS?"
print(f"\nQUERY: {query}")
ctx = pipeline.run(query)
print(f"Status: {ctx.state.value}")
print(f"SQL: {ctx.data.get('sql')}")
print(f"Assumptions: {ctx.data.get('assumptions', [])}")
print(f"Metrics: {ctx.data.get('semantic_resolution', {}).get('metrics')}")
print(f"Entities: {ctx.data.get('semantic_resolution', {}).get('entities')}")
if ctx.errors:
    print(f"Errors: {ctx.errors}")
