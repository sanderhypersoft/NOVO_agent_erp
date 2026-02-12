import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from pipeline_executor import PipelineExecutor
from semantic_dictionary import get_semantic_dictionary
from operational_dictionary import OperationalDictionary
from agent_state import AgentState

def run_canonical_tests():
    log_file = open("test_run.log", "w", encoding="utf-8")
    
    def log(msg):
        print(msg, flush=True)
        log_file.write(msg + "\n")

    log("="*60)
    log("AGENT ERP V2 - CANONICAL TEST SUITE")
    log("="*60)

    pipeline = PipelineExecutor(
        semantic_dictionary=get_semantic_dictionary(),
        operational_dictionary=OperationalDictionary()
    )

    test_cases = [
        {
            "id": 1,
            "name": "Faturamento do mês atual",
            "question": "Qual foi o faturamento do mês atual?",
            "expected_state": AgentState.OK,
            "min_score": 90
        },
        {
            "id": 2,
            "name": "Quantidade de vendas concluídas",
            "question": "Quantas vendas concluídas tivemos hoje?",
            "expected_state": AgentState.OK,
            "min_score": 90
        },
        {
            "id": 3,
            "name": "Ticket médio por cliente",
            "question": "Qual é o ticket médio por cliente no mês atual?",
            "expected_state": AgentState.PARTIAL,
            "min_score": 70
        },
        {
            "id": 4,
            "name": "Inadimplência atual",
            "question": "Qual é o valor da inadimplência hoje?",
            "expected_state": AgentState.OK,
            "min_score": 85
        },
        {
            "id": 5,
            "name": "Vendas do mês (Ambiguidade)",
            "question": "Quanto vendemos neste mês?",
            "expected_state": AgentState.AMBIGUOUS,
            "min_score": 0
        },
        {
            "id": 6,
            "name": "Performance por forma de pagamento",
            "question": "Qual a performance de vendas por forma de pagamento?",
            "expected_state": AgentState.PARTIAL,
            "min_score": 60
        },
        {
            "id": 7,
            "name": "Métrica inexistente",
            "question": "Qual o índice de felicidade dos clientes?",
            "expected_state": AgentState.FAIL,
            "min_score": 0
        },
        {
            "id": 8,
            "name": "Entidades incompatíveis",
            "question": "Total de vendas pagas por títulos a pagar",
            "expected_state": AgentState.FAIL,
            "min_score": 0
        }
    ]

    results = []
    
    for case in test_cases:
        log(f"\n[TEST {case['id']}] {case['name']}")
        log(f"Question: \"{case['question']}\"")
        
        try:
            context = pipeline.run(case['question'])
            
            passed_state = context.state == case['expected_state']
            passed_score = context.score >= case['min_score']
            
            status = "PASSED" if passed_state and passed_score else "FAILED"
            
            log(f"Status: {status}")
            log(f" - State: {context.state.value} (Expected: {case['expected_state'].value})")
            log(f" - Score: {context.score} (Min: {case['min_score']})")
            if context.data.get("sql"):
                log(f" - SQL: {context.data['sql'][:100]}...")
            
            results.append({
                "id": case['id'],
                "passed": passed_state and passed_score,
                "context": context
            })
            
        except Exception as e:
            log("Status: ERROR")
            log(f" - Error: {str(e)}")
            results.append({
                "id": case['id'],
                "passed": False,
                "error": str(e)
            })

    log("\n" + "="*60)
    log("FINAL SUMMARY")
    log("="*60)
    
    total = len(test_cases)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed
    
    log(f"Total Tests: {total}")
    log(f"Passed:      {passed} ({passed/total*100:.1f}%)")
    log(f"Failed:      {failed} ({failed/total*100:.1f}%)")
    log("="*60)
    
    log_file.close()

if __name__ == "__main__":
    run_canonical_tests()
