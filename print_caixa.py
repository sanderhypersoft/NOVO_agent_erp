import fdb

conn = fdb.connect(dsn=r'localhost:C:\Users\HYPERSOFT\Documents\agent-erp-mvp\FDB\DADOS.fdb', user='SYSDBA', password='masterkey', charset='WIN1252')
cur = conn.cursor()
cur.execute('SELECT FIRST 1 * FROM RECEITAS')
cols = [desc[0] for desc in cur.description]
print("RECEITAS Cols:")
for col in cols: print(col)

cur.execute('SELECT FIRST 1 * FROM CAIXA')
cols = [desc[0] for desc in cur.description]
print("CAIXA Cols:")
for col in cols: print(col)
