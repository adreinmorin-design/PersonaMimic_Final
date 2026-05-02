import sqlite3
import os

db_path = "persona_mimic.db"

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

columns_to_add = [
    ("description", "TEXT"),
    ("price", "INTEGER DEFAULT 0"),
    ("category", "TEXT"),
    ("sales_count", "INTEGER DEFAULT 0"),
    ("total_revenue", "INTEGER DEFAULT 0"),
    ("created_at", "DATETIME"),
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}")
        print(f"Added column: {col_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(f"Column {col_name} already exists.")
        else:
            print(f"Error adding {col_name}: {e}")

conn.commit()
conn.close()
print("Migration complete.")
