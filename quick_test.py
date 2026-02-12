import sys
sys.path.append("c:/Users/HYPERSOFT/Documents/agent_erp_v2")

from pipeline_executor import PipelineExecutor
from semantic_dictionary import get_semantic_dictionary
from operational_dictionary import OperationalDictionary

pipeline = PipelineExecutor(
    semantic_dictionary=get_semantic_dictionary(),
    operational_dictionary=OperationalDictionary()
)

# Query 1
print("QUERY 1: quais itens são mais consumidos por tecnicos nas OS?")
ctx1 = pipeline.run("quais itens são mais consumidos por tecnicos nas OS?")
print(f"Status: {ctx1.state.value}")
print(f"SQL: {ctx1.data.get('sql')}")
print(f"Assumptions: {ctx1.data.get('assumptions', [])}")
print(f"Errors: {ctx1.errors}")
print()

# Query 2  
print("QUERY 2: quais as contas a pagar e receber excluidas nos ultimos 15 dias e quem excluiu?")
ctx2 = pipeline.run("quais as contas a pagar e receber excluidas nos ultimos 15 dias e quem excluiu?")
print(f"Status: {ctx2.state.value}")
print(f"SQL: {ctx2.data.get('sql')}")
print(f"Assumptions: {ctx2.data.get('assumptions', [])}")
print(f"Errors: {ctx2.errors}")
