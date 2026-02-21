import fdb

conn = fdb.connect(dsn=r'localhost:C:\Users\HYPERSOFT\Documents\agent-erp-mvp\FDB\DADOS.fdb', user='SYSDBA', password='masterkey', charset='WIN1252')
cur = conn.cursor()
cur.execute('SELECT FIRST 1 * FROM PAGAS')
cols = [desc[0] for desc in cur.description]
print("PAGAS Cols:", cols)

cur.execute('SELECT FIRST 1 * FROM RECEBER_STATUS')
cols = [desc[0] for desc in cur.description]
print("RECEBER_STATUS Cols:", cols)
