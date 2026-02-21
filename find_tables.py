import fdb

conn = fdb.connect(dsn=r'localhost:C:\Users\HYPERSOFT\Documents\agent-erp-mvp\FDB\DADOS.fdb', user='SYSDBA', password='masterkey', charset='WIN1252')
cur = conn.cursor()
cur.execute("SELECT RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$VIEW_BLR IS NULL AND (RDB$SYSTEM_FLAG IS NULL OR RDB$SYSTEM_FLAG = 0)")
tables = [row[0].strip() for row in cur.fetchall()]
for t in tables:
    if 'REC' in t or 'BX' in t or 'BAIXA' in t or 'PAG' in t or 'CAIXA' in t:
        print(t)
