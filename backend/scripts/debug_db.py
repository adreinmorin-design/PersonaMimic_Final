import os
import sys

# Ensure backend is in path
sys.path.append(os.path.abspath("backend"))

from app.auth.service import auth_service
from app.core.paths import DATABASE_PATH
from app.database.database import SessionLocal, engine
from app.database.service import db_service


def test_init():
    print(f"DATABASE_PATH resolved as: {DATABASE_PATH}")
    print(f"Engine URL: {engine.url}")
    print("Pre-cleaning...")
    if os.path.exists("persona_mimic.db"):
        os.remove("persona_mimic.db")

    print("Initializing DB...")
    db_service.init_db()

    print("Checking for file...")
    if os.path.exists("persona_mimic.db"):
        print(f"SUCCESS: persona_mimic.db created at {os.path.abspath('persona_mimic.db')}")
    else:
        print("FAIL: persona_mimic.db NOT created.")

    print("Auto-onboarding...")
    db = SessionLocal()
    try:
        auth_service.auto_onboard(db)
        print("Onboarding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    test_init()
