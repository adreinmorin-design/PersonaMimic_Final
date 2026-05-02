import base64
import os
import re
import sqlite3
import sys

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

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


def update_env(key: str, value: str):
    env_path = ".env"
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        content = f.read()

    pattern = rf"^{key}=.*"
    replacement = f"{key}={value}"

    if re.search(pattern, content, re.MULTILINE):
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    else:
        content += f"\n{key}={value}"

    with open(env_path, "w") as f:
        f.write(content)


def finalize_migration():
    sqlite_path = "../persona_mimic.db"
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM system_settings WHERE key LIKE 'WHOP_%'")
    rows = cursor.fetchall()
    conn.close()

    for key, encrypted_value in rows:
        val = decrypt(encrypted_value)
        update_env(key.upper(), val)
        print(f"Updated .env with {key}")


if __name__ == "__main__":
    finalize_migration()
