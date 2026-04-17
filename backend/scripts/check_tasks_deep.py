from app.database.database import SessionLocal
from app.swarm.models import TaskQueue

db = SessionLocal()
try:
    tasks = db.query(TaskQueue).all()
    print(f"Total tasks: {len(tasks)}")
    for t in tasks[-20:]:
        print(f"ID: {t.id} | Brain: {t.brain_name} | Status: {t.status}")
finally:
    db.close()
