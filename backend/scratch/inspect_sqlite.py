import os
import sqlite3


def check_sqlite():
    sqlite_path = "../persona_mimic.db"
    if not os.path.exists(sqlite_path):
        print("SQLite not found")
        return

    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM system_settings WHERE key LIKE 'WHOP_%'")
    rows = cursor.fetchall()
    conn.close()

    for key, val in rows:
        print(f"{key}: {val[:30]}...")


if __name__ == "__main__":
    check_sqlite()
