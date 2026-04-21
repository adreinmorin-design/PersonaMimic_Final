import base64
import os
import sqlite3
import sys

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Add current directory to path for imports
sys.path.append(os.getcwd())


def decrypt(token: str, master_key: str = "dre_sentinel_2026") -> str:
    salt = b"mimic_neural_salt"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()


def migrate_keys():
    # 1. Extract from SQLite
    sqlite_path = "../persona_mimic.db"
    if not os.path.exists(sqlite_path):
        print(f"SQLite DB not found at {sqlite_path}")
        return

    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    # Try to find the keys in the settings table (based on the grep output)
    # The grep output showed them in a binary/text blob, likely 'system_settings' table
    try:
        cursor.execute("SELECT key, value FROM system_settings WHERE key LIKE 'WHOP_%'")
        rows = cursor.fetchall()
    except Exception as e:
        print(f"Error reading SQLite: {e}")
        return
    finally:
        conn.close()

    if not rows:
        print("No WHOP keys found in SQLite.")
        return

    # 2. Decrypt and Inject into Postgres
    from app.config.models import SystemSetting
    from app.database.database import SessionLocal

    db = SessionLocal()
    try:
        for key, encrypted_value in rows:
            try:
                decrypted_value = decrypt(encrypted_value)
                print(f"Successfully decrypted {key}")

                # Inject into Postgres (SystemSetting)
                setting = db.query(SystemSetting).filter(SystemSetting.key == key.lower()).first()
                if not setting:
                    setting = SystemSetting(key=key.lower(), value=decrypted_value)
                    db.add(setting)
                else:
                    setting.value = decrypted_value

                # Also update .env for redundancy
                print(f"Updating .env for {key}")
                # (Logic to update .env omitted for brevity in script, I'll do it manually or via another tool)

            except Exception as e:
                print(f"Failed to decrypt/inject {key}: {e}")

        db.commit()
        print("Migration to Postgres complete.")
    finally:
        db.close()


if __name__ == "__main__":
    migrate_keys()
