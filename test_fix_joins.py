
from semantic_dictionary import get_semantic_dictionary
from operational_dictionary import OperationalDictionary
from sql_builder import SQLBuilder
from agent_state import AgentContext, AgentState

def test_ticket_medio_join():
    print("TEST: Verifying Ticket Medio Join Condition")
    
    # Setup
    op_release = OperationalDictionary()
    semantic = get_semantic_dictionary()
    builder = SQLBuilder(semantic, op_release)
    
    # Mock Context
    mock_intent = {"type": "aggregation"}
    mock_semantic = {
        "metrics": ["ticket_medio"],
        "entities": ["cliente", "venda"],
        "states": ["venda_concluida"],
        "time_refs": [{"start": "2026-02-01", "end": "2026-02-05"}],
        "intent_type": "aggregation"
    }
    
    context = AgentContext(question="ticket medio por cliente")
    context.data["intent"] = mock_intent
    context.data["semantic_resolution"] = mock_semantic
    
    # Run
    result_context = builder.run(context)
    
    # Check
    sql = result_context.data.get("sql", "").upper()
    print(f"Generated SQL: {sql}")
    
    if "ON VENDAS.CLIENTE = CLIENTES.CODIGO" in sql:
        print("SUCCESS: Join condition is correct (CLIENTES.CODIGO)")
    else:
        print(f"FAILURE: Join condition invalid. SQL: {sql}")
        
    if "VENDAS.STATUS = 'F'" in sql:
        print("SUCCESS: Rule applied to VENDAS.STATUS")
    elif "CLIENTES.STATUS" in sql:
        print("FAILURE: Rule applied to CLIENTES (Wrong Table)")
        
    if "VENDAS.DATA BETWEEN" in sql:
        print("SUCCESS: Time filter applied to VENDAS.DATA")
    elif "CLIENTES.DT_CAD" in sql:  
        print("FAILURE: Time filter applied to CLIENTES.DT_CAD (Wrong Table)")

if __name__ == "__main__":
    test_ticket_medio_join()
