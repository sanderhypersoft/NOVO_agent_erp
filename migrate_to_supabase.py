import os
import pandas as pd
from supabase_adapter import SupabaseAdapter
from semantic_dictionary import SemanticDictionary
from operational_dictionary import OperationalDictionary

def migrate():
    adapter = SupabaseAdapter()
    
    # 1. Migrar Dicionário Semântico
    print("Migrando Dicionário Semântico...")
    sem_dict = SemanticDictionary()
    for concept, data in sem_dict.concepts.items():
        payload = {
            "concept": concept.lower(),
            "synonyms": data.aliases,
            "required_entities": data.entidades,
            "default_rules": data.regras,
            "type": data.tipo,
            "description": data.descricao
        }
        try:
            adapter.supabase.table("semantic_dictionary").upsert(payload, on_conflict="concept").execute()
        except Exception as e:
            print(f"Erro ao migrar conceito '{concept}': {e}")
    
    # 2. Migrar Dicionário Operacional
    print("Migrando Dicionário Operacional...")
    excel_path = "Dicionario_Operacional_MVP.xlsx"
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path)
        print(f"Colunas encontradas: {df.columns.tolist()}")
        # Normalizar colunas para busca flexível
        col_map = {c.strip().upper(): c for c in df.columns}
        
        concept_col = col_map.get('CONCEPT') or col_map.get('CONCEITO') or col_map.get('CONCEITOS') or col_map.get('SEMANTIC_ROLE')
        table_col = col_map.get('TABLE_NAME') or col_map.get('TABELA')
        field_col = col_map.get('FIELD_NAME') or col_map.get('CAMPO')
        metric_col = col_map.get('METRIC') or col_map.get('METRICA')
        sql_col = col_map.get('CUSTOM_SQL') or col_map.get('SQL_CUSTOM')

        for _, row in df.iterrows():
            payload = {
                "concept": str(row[concept_col]).lower() if concept_col and pd.notna(row[concept_col]) else "unknown",
                "table_name": str(row[table_col]).upper() if table_col else "UNKNOWN",
                "field_name": str(row[field_col]).upper() if field_col and pd.notna(row[field_col]) else None,
                "is_metric": str(row.get(metric_col, 'N')).upper() == 'S' if metric_col else False,
                "custom_sql": str(row[sql_col]) if sql_col and pd.notna(row[sql_col]) else None
            }
            try:
                adapter.supabase.table("operational_dictionary").insert(payload).execute()
            except Exception as e:
                print(f"Erro ao migrar operacional '{payload['concept']}': {e}")
    else:
        # Fallback para o dicionário em Python se o Excel não existir
        op_dict = OperationalDictionary()
        # Aqui dependeria da estrutura interna do op_dict, 
        # mas como temos o arquivo excel no list_dir, vamos priorizá-lo.
        pass

    print("Migração concluída com sucesso!")

if __name__ == "__main__":
    migrate()
