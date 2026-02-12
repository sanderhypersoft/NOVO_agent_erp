
import sys
import os

# Adiciona o diretório atual ao path
sys.path.append(os.getcwd())

from sql_builder import SQLBuilder
from operational_dictionary import OperationalDictionary
from semantic_dictionary import get_semantic_dictionary
from agent_state import AgentState

# Mock Context
class MockContext:
    def __init__(self, intent_type, metrics, entities, modifiers=None):
        self.state = AgentState.PARTIAL # Default valid state
        self.data = {
            "intent": {"type": intent_type, "raw_question": "Test Query"},
            "semantic_resolution": {
                "intent_type": intent_type,
                "metrics": metrics,
                "entities": entities,
                "states": ["venda_concluida"], # Default state for safety
                "time_refs": [],
                "modifiers": modifiers or []
            },
            "rule_warnings": []
        }
        self.errors = []

def run_test():
    with open("test_generation_log.txt", "w", encoding="utf-8") as log_file:
        sys.stdout = log_file
        print("Initializing components...")
        semantic_dict = get_semantic_dictionary()
        operational_dict = OperationalDictionary() # Will load schema from default location
        builder = SQLBuilder(semantic_dict, operational_dict)

        tests = [
            {
                "name": "Total Faturamento (No Group By)",
                "intent": "aggregation",
                "metrics": ["faturamento"],
                "entities": ["venda"],
                "expected_contains": ["SUM(VENDAS.TOTAL)", "FROM VENDAS", "STATUS = 'F'"],
                "expected_not_contains": ["GROUP BY"]
            },
            {
                "name": "Faturamento por Vendedor (Group By Explicit)",
                "intent": "aggregation",
                "metrics": ["faturamento"],
                "entities": ["vendedor"], # Vendedor implies grouping if metric is present
                "expected_contains": ["SUM(VENDAS.TOTAL)", "GROUP BY", "VENDEDOR.NOME"],
            },
            {
                "name": "Ticket Medio Global",
                "intent": "aggregation",
                "metrics": ["ticket_medio"],
                "entities": ["venda"],
                "expected_contains": ["AVG(VENDAS.TOTAL)", "FROM VENDAS"]
            },
            {
                "name": "Listagem Simples (Sem Metrica)",
                "intent": "detail",
                "metrics": [],
                "entities": ["cliente"],
                "expected_contains": ["SELECT", "FROM CLIENTES", "CLIENTES.CODIGO"] # First field in schema
            }
        ]

        print(f"\nRunning {len(tests)} tests...\n")
        
        passed = 0
        for t in tests:
            print(f"--- Test: {t['name']} ---")
            ctx = MockContext(t['intent'], t['metrics'], t['entities'])
            
            try:
                result_ctx = builder.run(ctx)
                sql = result_ctx.data.get("sql", "")
                print(f"Generated SQL: {sql}")
                
                if result_ctx.state == AgentState.FAIL:
                    print(f"FAILED: Agent State is FAIL. Errors: {result_ctx.errors}")
                    continue

                # Verification
                failures = []
                for item in t.get("expected_contains", []):
                    if item not in sql:
                        failures.append(f"Missing expected string: '{item}'")
                
                for item in t.get("expected_not_contains", []):
                    if item in sql:
                        failures.append(f"Found forbidden string: '{item}'")

                if failures:
                    print("FAILED Validation:")
                    for f in failures: print(f"  - {f}")
                else:
                    print("PASSED")
                    passed += 1

            except Exception as e:
                print(f"CRITICAL ERROR: {e}")
                import traceback
                traceback.print_exc()

        print(f"\nSummary: {passed}/{len(tests)} passed.")
        sys.stdout = sys.__stdout__ # Reset

if __name__ == "__main__":
    run_test()
