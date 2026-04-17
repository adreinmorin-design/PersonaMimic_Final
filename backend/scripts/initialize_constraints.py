import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config.service import config_service
from app.database.database import SessionLocal


def seed_constraints():
    db = SessionLocal()
    try:
        constraints = {
            "synthesis_probability": "0.5",
            "synthesis_whitelist": "Phoenix Channels, Appsmith DSL, Django Channels, Tornado Websockets, Stripe API SDK, React Fiber DAG, Supabase Realtime Sync",
            "min_forensic_score": "0.75",
            "max_active_brains": "5",
            "daily_token_quota": "1000000",
        }

        for key, value in constraints.items():
            existing = config_service.get_setting(db, key)
            if existing is None:
                print(f"Seeding {key} = {value}")
                config_service.update_setting(db, key, value)
            else:
                print(f"Setting {key} already exists: {existing}")

        print("Constraint seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_constraints()
