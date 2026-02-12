import json
import os

def extract_key_fields():
    schema_path = 'master_schema.json'
    if not os.path.exists(schema_path):
        print(f"Error: {schema_path} not found")
        return

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    tables_data = schema.get('tables', {})
    targets = [
        'ORDEMSERVICOS', 'ITENSOS', 'EXC_ORDEMSERVICOS', 'EXC_ITENSOS',
        'PAGAR', 'EXC_PAGAR', 'RECEBER', 'EXC_RECEBER', 
        'USUARIOS', 'VENDEDOR', 'LOGTABELAS', 'LOGSYS'
    ]
    
    with open('field_mapping.txt', 'w', encoding='utf-8') as f_out:
        f_out.write('CORE FIELD MAPPING\n==================\n')
        for t in targets:
            f_out.write(f'\n--- {t} ---\n')
            cols = tables_data.get(t, [])
            for c in cols:
                field = c.get('field', 'N/A')
                role = c.get('role', 'N/A')
                meaning = c.get('meaning', 'N/A')
                f_out.write(f'  - {field}: {role} ({meaning})\n')
    
    print("✅ Field mapping saved to field_mapping.txt")

if __name__ == "__main__":
    extract_key_fields()
