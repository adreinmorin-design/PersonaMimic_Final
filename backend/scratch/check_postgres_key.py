from app.config.models import SystemSetting
from app.database.database import SessionLocal


def check_key():
    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter(SystemSetting.key == "whop_api_key").first()
        if setting:
            print(f"FOUND: {setting.value[:10]}...")
        else:
            print("NOT FOUND")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    check_key()
