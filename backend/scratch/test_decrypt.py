import base64
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


def test_decrypt():
    sqlite_path = "../persona_mimic.db"
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM system_settings WHERE key LIKE 'WHOP_%'")
    rows = cursor.fetchall()
    conn.close()

    for key, val in rows:
        dec = decrypt(val)
        print(f"{key} (DECRYPTED): {dec[:15]}...")


if __name__ == "__main__":
    test_decrypt()
