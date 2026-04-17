from app.database.database import SessionLocal
from app.swarm.models import TaskQueue

db = SessionLocal()
try:
    processed = (
        db.query(TaskQueue)
        .filter(TaskQueue.status == "failed")
        .update({"status": "correction_needed"})
    )
    db.commit()
    print(f"Successfully converted {processed} failed tasks to correction_needed in Postgres.")
finally:
    db.close()
