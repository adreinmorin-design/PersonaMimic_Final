import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.database import SessionLocal
from app.swarm.models import TaskQueue


def inject_task():
    db = SessionLocal()
    try:
        task = TaskQueue(
            brain_name="Dre",
            task_type="production",
            payload=json.dumps(
                {
                    "niche": "Reverse Engineering",
                    "goal": "Reverse engineer Phoenix Channels and Appsmith DSL industrial archetypes into functional studio-grade code.",
                    "quality_priority": True,
                    "branding_flair": "© 2026 Dre's Autonomous Neural Interface",
                }
            ),
            status="pending",
        )
        db.add(task)
        db.commit()
        print(f"[SUCCESS] Injected Reverse Engineering task. Task ID: {task.id}")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to inject task: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    inject_task()
