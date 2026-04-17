import json
import os
import sys
import time

# Add parent directory to path to find 'app' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.database import SessionLocal
from app.swarm.models import TaskQueue


def run_live_test():
    print("--- PERSONAMIMIC LIVE END-TO-END TEST ---")
    db = SessionLocal()
    try:
        # 1. Inject Test Task
        task = TaskQueue(
            brain_name="Dre",
            task_type="production",
            payload=json.dumps(
                {
                    "niche": "Branded Neural Optimization Tool",
                    "goal": "Build and publish a studio-grade, professional asset with 'Dre Branding Flair'.",
                    "quality_priority": True,
                }
            ),
            status="pending",
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        print(f"[OK] Injected Task ID: {task.id}")

        print("[WAIT] Waiting for Brain 'Dre' to pick up the task...")
        start_time = time.time()
        timeout = 60  # Increased timeout for production launch
        while time.time() - start_time < timeout:
            db.refresh(task)
            if task.status == "running":
                print(f"[SUCCESS] Brain 'Dre' is now RUNNING Task ID: {task.id}")
                break
            time.sleep(2)
        else:
            print("[FAIL] Task was not picked up. Ensure the orchestrator is running.")
            return

        print(
            "\n[INFO] The AI is now building the product. This loop involves research, coding, and documenting."
        )
        print("[INFO] Once finished, it will attempt Whop publishing if configured.")

    except Exception as e:
        print(f"[ERROR] Live test failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_live_test()
