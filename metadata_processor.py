import pandas as pd
import json
import os

def process_metadata(csv_path, output_json):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Fill missing table names (forward fill)
    df['TABLE_NAME'] = df['TABLE_NAME'].ffill()
    
    schema = {
        "metadata": {
            "total_tables": 0,
            "source": os.path.basename(csv_path)
        },
        "tables": {}
    }
    
    unique_tables = df['TABLE_NAME'].unique()
    schema["metadata"]["total_tables"] = len(unique_tables)
    
    for table in unique_tables:
        table_df = df[df['TABLE_NAME'] == table]
        fields = []
        
        for _, row in table_df.iterrows():
            # Skip rows where FIELD_NAME is placeholder or header-like (if any)
            if pd.isna(row['FIELD_NAME']) or row['FIELD_NAME'] == 'FIELD_NAME':
                continue
                
            def safe_float(val):
                if pd.isna(val): return 0.0
                try:
                    # Try direct conversion
                    return float(val)
                except ValueError:
                    # Try extracting first numeric part (e.g., "0.99 says" -> "0.99")
                    try:
                        import re
                        match = re.search(r"[-+]?\d*\.\d+|\d+", str(val))
                        if match:
                            return float(match.group())
                    except:
                        pass
                    return 0.0

            field_data = {
                "field": str(row['FIELD_NAME']),
                "type": str(row['FIELD_TYPE']),
                "role": str(row['SEMANTIC_ROLE']),
                "meaning": str(row['BUSINESS_MEANING']),
                "join_hint": str(row['JOIN_HINT']) if not pd.isna(row['JOIN_HINT']) else None,
                "confidence": safe_float(row['CONFIDENCE'])
            }
            fields.append(field_data)
        
        schema["tables"][table] = fields
    
    # Write to JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully processed {len(unique_tables)} tables into {output_json}")

if __name__ == "__main__":
    base_dir = r"c:\Users\HYPERSOFT\Documents\agent_erp_v2"
    csv_file = os.path.join(base_dir, "full_sheet_DICIONARIO_TABELAS.csv")
    json_file = os.path.join(base_dir, "master_schema.json")
    process_metadata(csv_file, json_file)
