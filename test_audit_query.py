
from pipeline_executor import PipelineExecutor
from semantic_dictionary import get_semantic_dictionary
from operational_dictionary import OperationalDictionary
from agent_state import AgentState

def test_audit_query():
    print("TEST: Verifying Audit Query (Exclusion + User + Last)")
    
    # Setup
    pipeline = PipelineExecutor(get_semantic_dictionary(), OperationalDictionary())
    
    # Query
    q = "Quais foram as ultimas contas a pagar excluídas"
    print(f"Question: {q}")
    
    context = pipeline.run(q)
    
    print(f"State: {context.state}")
    print(f"Errors: {context.errors}")
    
    if context.state == AgentState.OK or context.state == AgentState.PARTIAL:
        sql = context.data.get("sql", "").upper()
        print(f"SQL: {sql}")
        
        if "SELECT FIRST 10" in sql:
            print("SUCCESS: LIMIT 10 (FIRST 10) applied")
        else:
            print("FAILURE: LIMIT missing")
            
        if "ORDER BY" in sql:
            print("SUCCESS: ORDER BY applied")
        else:
            print("FAILURE: ORDER BY missing")
            
        if "PAGAR.STATUS = 'E'" in sql or "PAGAR.TIPO = 'E'" in sql: # Check rule application (assuming 'E' for exclusion)
            print("SUCCESS: Exclusion rule applied")
        else: 
            # Check if default status rule from semantic dictionary is applied
            # Note: "exclusao_financeira" maps to "TIPO = 'E'" in OperationalDictionary
            if "TIPO = 'E'" in sql:
                 print("SUCCESS: Exclusion rule TIPO='E' applied")
            else:
                 print("FAILURE: Exclusion rule missing")

    else:
        print("FAILURE: Pipeline blocked")

if __name__ == "__main__":
    test_audit_query()
