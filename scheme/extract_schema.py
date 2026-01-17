import sqlite3
import json

conn = sqlite3.connect("data/chinook.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

schema = {}

for t in tables:
    table = t[0]
    cursor.execute(f"PRAGMA table_info({table});")
    schema[table] = [col[1] for col in cursor.fetchall()]

with open("schema/schema.json", "w") as f:
    json.dump(schema, f, indent=2)

print("Schema extracted successfully")
