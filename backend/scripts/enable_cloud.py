import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from app.config.models import SystemSetting
from app.database.database import SessionLocal


def enable_cloud():
    print("[*] Contacting Database to Force Cloud Engine Override...")
    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter(SystemSetting.key == "use_cloud").first()
        if not setting:
            setting = SystemSetting(key="use_cloud", value="True")
            db.add(setting)
        else:
            setting.value = "True"
        db.commit()
        print("[SUCCESS] Cloud Neural Engine toggled to TRUE (Groq/Llama-3.3).")
    except Exception as e:
        print(f"[ERR] {e}")
    finally:
        db.close()


if __name__ == "__main__":
    enable_cloud()
