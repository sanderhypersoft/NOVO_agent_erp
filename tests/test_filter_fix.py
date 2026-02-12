
import sys
import os

sys.path.append(os.getcwd())

from sql_builder import SQLBuilder
from operational_dictionary import OperationalDictionary
from semantic_dictionary import get_semantic_dictionary
from agent_state import AgentState

class MockContext:
    def __init__(self, intent_type, metrics, entities, modifiers=None):
        self.state = AgentState.PARTIAL
        self.data = {
            "intent": {"type": intent_type, "raw_question": "Test Query"},
            "semantic_resolution": {
                "intent_type": intent_type,
                "metrics": metrics,
                "entities": entities,
                "states": ["venda_concluida"],
                "time_refs": [],
                "modifiers": modifiers or []
            },
            "rule_warnings": []
        }
        self.errors = []

def test_filter_application():
    """
    Testa se o filtro STATUS = 'F' é aplicado na tabela correta.
    
    Bug anterior: "Faturamento por Vendedor" aplicava VENDEDOR.STATUS = 'F'
    Comportamento correto: Deve aplicar VENDAS.STATUS = 'F' (tabela de contexto da métrica)
    """
    print("Testing Filter Application Fix...")
    
    semantic_dict = get_semantic_dictionary()
    operational_dict = OperationalDictionary()
    builder = SQLBuilder(semantic_dict, operational_dict)
    
    # Caso de teste: Faturamento por Vendedor
    ctx = MockContext("aggregation", ["faturamento"], ["vendedor"])
    result_ctx = builder.run(ctx)
    sql = result_ctx.data.get("sql", "")
    
    print(f"\nGenerated SQL:\n{sql}\n")
    
    # Verificações
    checks = {
        "✅ Contém SUM(VENDAS.TOTAL)": "SUM(VENDAS.TOTAL)" in sql,
        "✅ Contém GROUP BY": "GROUP BY" in sql,
        "✅ Contém VENDEDOR.NOME": "VENDEDOR.NOME" in sql,
        "🔍 CRITICAL: Usa VENDAS.STATUS (não VENDEDOR.STATUS)": "VENDAS.STATUS = 'F'" in sql,
        "❌ NÃO deve ter VENDEDOR.STATUS": "VENDEDOR.STATUS" not in sql
    }
    
    all_passed = True
    for check, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check}")
        if not result:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 SUCESSO: Filtro aplicado na tabela correta!")
    else:
        print("⚠️ FALHA: Filtro ainda sendo aplicado incorretamente")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = test_filter_application()
    sys.exit(0 if success else 1)
