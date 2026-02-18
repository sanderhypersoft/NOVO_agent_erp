import fdb
import os
from typing import List, Dict, Any

class FirebirdExecutor:
    def __init__(self):
        # Configuração baseada no ambiente legado encontrado
        # Usamos raw string para caminhos Windows
        self.dsn = os.environ.get("FIREBIRD_DSN", r'localhost:C:\Users\HYPERSOFT\Documents\agent-erp-mvp\FDB\DADOS.fdb')
        self.user = os.environ.get("FIREBIRD_USER", "SYSDBA")
        self.password = os.environ.get("FIREBIRD_PASSWORD", "masterkey")
        self.charset = "WIN1252"
        self._conn = None

    def execute(self, sql: str) -> List[Dict[str, Any]]:
        """Executa SQL no Firebird e retorna lista de dicionários"""
        if not sql:
            return []
            
        try:
            conn = fdb.connect(
                dsn=self.dsn,
                user=self.user,
                password=self.password,
                charset=self.charset
            )
            cur = conn.cursor()
            cur.execute(sql)
            
            # Se não for SELECT, apenas commita e retorna vazio
            if not cur.description:
                conn.commit()
                conn.close()
                return []
                
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            
            results = []
            for row in rows:
                # Converte tipos especiais (como Decimal ou datas) para string se necessário
                results.append(dict(zip(cols, [str(v) if v is not None else None for v in row])))
            
            conn.close()
            return results
        except Exception as e:
            print(f"ERROR FirebirdExecutor: {e}")
            raise e
