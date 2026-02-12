"""
Script to analyze master_schema.json and categorize all 187 tables
"""
import json
from collections import defaultdict

# Load schema
with open('master_schema.json', 'r', encoding='utf-8') as f:
    schema = json.load(f)

tables = schema.get('tables', {})

# Categorize tables
categories = defaultdict(list)

for table_name in sorted(tables.keys()):
    # Financial
    if any(x in table_name for x in ['PAGAR', 'RECEBER', 'CAIXA', 'BANCO', 'CHEQUE', 'CARTAO', 'BORDERO']):
        categories['FINANCEIRO'].append(table_name)
    
    # Sales
    elif any(x in table_name for x in ['VENDAS', 'ITENSV', 'CUPOM', 'NOTA']):
        categories['VENDAS'].append(table_name)
    
    # Customers/Suppliers
    elif any(x in table_name for x in ['CLIENTES', 'FORNEC', 'AGENTES']):
        categories['CADASTROS'].append(table_name)
    
    # Service Orders
    elif any(x in table_name for x in ['ORDEMSERVICOS', 'ITENSO', 'OS_']):
        categories['ORDEM_SERVICO'].append(table_name)
    
    # Inventory
    elif any(x in table_name for x in ['ESTOQUE', 'ALM_', 'PRODUTOS', 'MOVIESTOQUE']):
        categories['ESTOQUE'].append(table_name)
    
    # Exclusions/Audit
    elif table_name.startswith('EXC_'):
        categories['EXCLUSOES'].append(table_name)
    
    # Contracts
    elif 'CONTRATO' in table_name or 'CONVENIO' in table_name:
        categories['CONTRATOS'].append(table_name)
    
    # Configuration
    elif any(x in table_name for x in ['CONFIG', 'EMPRESAS', 'USUARIOS', 'FILTRO']):
        categories['CONFIGURACAO'].append(table_name)
    
    else:
        categories['OUTROS'].append(table_name)

# Print categorization
print("="*80)
print("CATEGORIZAÇÃO DAS 187 TABELAS")
print("="*80)

for category, table_list in sorted(categories.items()):
    print(f"\n### {category} ({len(table_list)} tabelas)")
    for table in table_list:
        print(f"  - {table}")

# Save to file
with open('table_categorization.txt', 'w', encoding='utf-8') as f:
    f.write("CATEGORIZAÇÃO DAS 187 TABELAS\n")
    f.write("="*80 + "\n\n")
    for category, table_list in sorted(categories.items()):
        f.write(f"\n### {category} ({len(table_list)} tabelas)\n")
        for table in table_list:
            f.write(f"  - {table}\n")

print(f"\n\n✅ Categorização salva em: table_categorization.txt")
