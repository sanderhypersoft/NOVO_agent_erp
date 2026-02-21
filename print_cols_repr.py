import fdb

conn = fdb.connect(dsn=r'localhost:C:\Users\HYPERSOFT\Documents\agent-erp-mvp\FDB\DADOS.fdb', user='SYSDBA', password='masterkey', charset='WIN1252')
cur = conn.cursor()

for t in ["RECEBER", "RECEBER_STATUS", "RECEBER_PARC", "PAGAS"]:
    try:
        cur.execute(f"SELECT FIRST 1 * FROM {t}")
        cols = [desc[0] for desc in cur.description]
        print(f"--- {t} ---")
        for col in cols: print(repr(col.strip()))
    except Exception as e:
        print(f"Table {t} failed: {e}")
