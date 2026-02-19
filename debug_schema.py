import json
import os

schema_path = "master_schema.json"
with open(schema_path, "r", encoding="utf-8") as f:
    schema = json.load(f)

tables = schema.get("tables", {})
target_tables = ["PAGAR", "EXC_PAGAR", "EXC_USUARIO", "USUARIOS"]

for t in target_tables:
    keys = [k for k in tables.keys() if k.upper() == t]
    if keys:
        k = keys[0]
        print(f"\n--- Table: {k} ---")
        fields = [f["field"] for f in tables[k]]
        # Print fields in chunks to avoid truncation if it's a display issue
        for i in range(0, len(fields), 20):
            print(", ".join(fields[i:i+20]))
    else:
        print(f"\n--- Table {t} NOT FOUND ---")
