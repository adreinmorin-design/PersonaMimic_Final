import base64
import os
import sqlite3

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Master Key for Studio
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
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM system_settings WHERE key LIKE 'WHOP_%'")
    rows = cursor.fetchall()
    conn.close()

    env_path = ".env"
    with open(env_path) as f:
        lines = f.readlines()

    new_lines = []
    found_keys = {}
    for key, enc_val in rows:
        found_keys[key.upper()] = decrypt(enc_val)

    for line in lines:
        if line.startswith("WHOP_API_KEY="):
            new_lines.append(f"WHOP_API_KEY={found_keys.get('WHOP_API_KEY')}\n")
        elif line.startswith("WHOP_COMPANY_ID="):
            new_lines.append(f"WHOP_COMPANY_ID={found_keys.get('WHOP_COMPANY_ID')}\n")
        else:
            new_lines.append(line)

    with open(env_path, "w") as f:
        f.writelines(new_lines)

    print(f"Force Injected {len(found_keys)} keys into {os.path.abspath(env_path)}")


if __name__ == "__main__":
    force_inject()
