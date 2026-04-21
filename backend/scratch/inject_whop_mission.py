import json
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from app.database.database import SessionLocal
from app.swarm.models import TaskQueue


def inject_mission():
    db = SessionLocal()
    payload = {
        "niche": "Whop Digital Distribution",
        "product_name": "Whop_Nexus_Engine",
        "specs": "Complete Whop-integrated SaaS with FastAPI backend (DDD, type hints) and Vite React frontend. Must include Whop Webhook handlers and a secure digital delivery loop.",
    }
    task = TaskQueue(
        brain_name="MasterBrain", task_type="mission", payload=json.dumps(payload), status="pending"
    )
    db.add(task)
    db.commit()
    print(f"Mission Injected: Task #{task.id}")
    db.close()


if __name__ == "__main__":
    inject_mission()
