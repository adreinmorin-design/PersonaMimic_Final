import sqlite3
import os

db_path = "persona_mimic.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT key, value FROM system_settings WHERE key IN ('use_cloud', 'OLLAMA_CLOUD_KEY', 'GROQ_API_KEY', 'model');"
        )
        rows = cursor.fetchall()
        for row in rows:
            print(f"{row[0]}: {row[1]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print("DB not found")
