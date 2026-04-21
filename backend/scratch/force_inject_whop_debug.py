import base64
import os
import sqlite3

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MASTER_KEY = "dre_sentinel_2026"


def decrypt(token: str) -> str:
    salt = b"mimic_neural_salt"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(MASTER_KEY.encode()))
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()


def force_inject():
    sqlite_path = "../persona_mimic.db"
    if not os.path.exists(sqlite_path):
        print(f"Error: {sqlite_path} not found")
        return

    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM system_settings WHERE key LIKE 'WHOP_%'")
    rows = cursor.fetchall()
    conn.close()

    env_path = ".env"
    if not os.path.exists(env_path):
        print(f"Error: {env_path} not found")
        return

    with open(env_path) as f:
        lines = f.readlines()

    found_keys = {}
    for key, enc_val in rows:
        found_keys[key.upper()] = decrypt(enc_val)

    with open(env_path, "w") as f:
        for line in lines:
            if "WHOP_API_KEY=" in line:
                val = found_keys.get("WHOP_API_KEY")
                f.write(f"WHOP_API_KEY={val}\n")
                print(f"DEBUG: Writing WHOP_API_KEY={val[:10]}...")
            elif "WHOP_COMPANY_ID=" in line:
                val = found_keys.get("WHOP_COMPANY_ID")
                f.write(f"WHOP_COMPANY_ID={val}\n")
                print(f"DEBUG: Writing WHOP_COMPANY_ID={val[:10]}...")
            else:
                f.write(line)

    print(f"DONE. Injected into {os.path.abspath(env_path)}")


if __name__ == "__main__":
    force_inject()
