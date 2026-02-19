import os
from typing import List, Dict

class FirebirdSchemaMapper:
    """
    Responsável por extrair metadados reais do Firebird via catálogo RDB$.
    """
    def __init__(self):
        self.db_path = os.environ.get("FIREBIRD_DB_PATH", r"C:\Users\HYPERSOFT\Documents\agent-erp-mvp\FDB\DADOS.fdb")

    def get_tables(self) -> List[str]:
        sql = """
            SELECT RDB$RELATION_NAME 
            FROM RDB$RELATIONS 
            WHERE RDB$SYSTEM_FLAG = 0 AND RDB$VIEW_BLR IS NULL
            ORDER BY RDB$RELATION_NAME
        """
        results = self._execute(sql)
        return [r["RDB$RELATION_NAME"].strip() for r in results]

    def get_columns(self, table_name: str) -> List[Dict]:
        sql = f"""
            SELECT 
                RF.RDB$FIELD_NAME AS FIELD_NAME,
                F.RDB$FIELD_TYPE AS FIELD_TYPE,
                F.RDB$FIELD_LENGTH AS FIELD_LENGTH
            FROM RDB$RELATION_FIELDS RF
            JOIN RDB$FIELDS F ON RF.RDB$FIELD_SOURCE = F.RDB$FIELD_NAME
            WHERE RF.RDB$RELATION_NAME = '{table_name.upper()}'
            ORDER BY RF.RDB$POSITION
        """
        results = self._execute(sql)
        mapped = []
        for r in results:
            type_code = r["FIELD_TYPE"]
            type_name = self._map_type(type_code)
            mapped.append({
                "field": r["FIELD_NAME"].strip(),
                "type": type_name,
                "raw_type": type_code
            })
        return mapped

    def _map_type(self, code: int) -> str:
        types = {
            7: "SMALLINT",
            8: "INTEGER",
            10: "FLOAT",
            12: "DATE",
            13: "TIME",
            14: "CHAR",
            16: "BIGINT",
            27: "DOUBLE PRECISION",
            35: "TIMESTAMP",
            37: "VARCHAR",
            261: "BLOB"
        }
        return types.get(code, "UNKNOWN")

    def _execute(self, sql: str) -> List[Dict]:
        try:
            import fdb
            conn = fdb.connect(
                dsn=self.db_path,
                user=os.environ.get("FIREBIRD_USER", "SYSDBA"),
                password=os.environ.get("FIREBIRD_PASS", "masterkey"),
                charset='WIN1252'
            )
            cur = conn.cursor()
            cur.execute(sql)
            
            columns = [column[0] for column in cur.description]
            results = []
            for row in cur.fetchall():
                results.append(dict(zip(columns, row)))
            
            conn.close()
            return results
        except Exception as e:
            print(f"Erro ao acessar Firebird Metadata: {e}")
            return []

if __name__ == "__main__":
    mapper = FirebirdSchemaMapper()
    print("Testando mapeamento de tabelas...")
    tables = mapper.get_tables()
    print(f"Tabelas encontradas: {len(tables)}")
    if tables:
        print(f"Campos de {tables[0]}:")
        print(mapper.get_columns(tables[0]))
