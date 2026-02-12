"""
Teste de Queries - Simulação de Cliente Leigo
"""
import sys
import os
sys.path.append(os.getcwd())

from pipeline_executor import PipelineExecutor
from semantic_dictionary import get_semantic_dictionary
from operational_dictionary import OperationalDictionary
import json

# Inicializar pipeline
pipeline = PipelineExecutor(
    semantic_dictionary=get_semantic_dictionary(),
    operational_dictionary=OperationalDictionary()
)

def test_query(question):
    print("\n" + "="*80)
    print(f"PERGUNTA: {question}")
    print("="*80)
    
    context = pipeline.run(question)
    
    print(f"\n📊 STATUS: {context.state.value}")
    print(f"🎯 CONFIDENCE: {context.score}")
    
    if context.data.get("assumptions"):
        print(f"\n💡 ASSUMPTIONS:")
        for assumption in context.data["assumptions"]:
            print(f"   - {assumption}")
    
    if context.data.get("sql"):
        print(f"\n✅ SQL GERADO:")
        print(f"   {context.data['sql']}")
    else:
        print(f"\n❌ SQL NÃO GERADO")
    
    if context.errors:
        print(f"\n⚠️ ERRORS:")
        for error in context.errors:
            print(f"   - {error}")
    
    if context.warnings:
        print(f"\n⚠️ WARNINGS:")
        for warning in context.warnings:
            print(f"   - {warning}")
    
    print(f"\n📋 SEMANTIC RESOLUTION:")
    semantic = context.data.get("semantic_resolution", {})
    print(f"   Metrics: {semantic.get('metrics', [])}")
    print(f"   Entities: {semantic.get('entities', [])}")
    print(f"   States: {semantic.get('states', [])}")
    print(f"   Time Refs: {semantic.get('time_refs', [])}")
    
    return context

if __name__ == "__main__":
    # Redirecionar output para arquivo
    import sys
    original_stdout = sys.stdout
    with open("customer_queries_results.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        
        print("\n🧪 TESTE DE QUERIES - MODO CLIENTE LEIGO")
        print("="*80)
        
        # Query 1: Itens mais consumidos por técnicos nas OS
        test_query("quais itens são mais consumidos por tecnicos nas OS?")
        
        # Query 2: Contas excluídas nos últimos 15 dias
        test_query("quais as contas a pagar e receber excluidas nos ultimos 15 dias e quem excluiu?")
        
        print("\n" + "="*80)
        print("FIM DOS TESTES")
        print("="*80)
    
    sys.stdout = original_stdout
    print("✅ Resultados salvos em: customer_queries_results.txt")
