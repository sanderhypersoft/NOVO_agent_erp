import sys
import os

# Use the current directory as base
sys.path.append(os.getcwd())

from api import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_migration_success():
    print("Verificando se a API migrada está respondendo corretamente...")
    
    # 1. Health Check
    res = client.get("/")
    print(f"Health Check: {res.json()}")
    assert res.json()["status"] == "online"

    # 2. Query Test
    print("\nTestando query 'Quanto faturamento hoje?'...")
    payload = {"question": "Quanto faturamento hoje?"}
    res = client.post("/agent/query", json=payload)
    data = res.json()
    
    print(f"Status: {data.get('status')}")
    print(f"SQL: {data.get('sql')}")
    print(f"Confiança: {data.get('confidence')}%")
    
    assert data.get("status") == "OK"
    assert "SUM(VALOR_TOTAL)" in data.get("sql")
    assert "VENDAS.DATA_EMISSAO" in data.get("sql")

    print("\nTestando Join 'Produtos vendidos hoje'...")
    payload = {"question": "Produtos vendidos hoje"}
    res = client.post("/agent/query", json=payload)
    data = res.json()
    
    print(f"Status: {data.get('status')}")
    print(f"SQL: {data.get('sql')}")
    
    assert "JOIN ITENS_VENDA" in data.get("sql")
    assert "JOIN VENDAS" in data.get("sql")

    print("\n✅ MIGRAÇÃO VERIFICADA COM SUCESSO!")

if __name__ == "__main__":
    test_migration_success()
