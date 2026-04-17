import os
import sys

# Add parent directory to path to find 'app' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.database import SessionLocal
from app.products.models import Product
from app.swarm.models import TaskQueue


def main():
    db = SessionLocal()
    try:
        print("--- LATEST TASKS ---")
        tasks = db.query(TaskQueue).order_by(TaskQueue.id.desc()).limit(5).all()
        for t in tasks:
            print(f"Task {t.id}: {t.brain_name} (Status: {t.status}, Created: {t.created_at})")

        if not tasks:
            print("No tasks found.")

        print("\n--- LATEST PRODUCTS ---")
        products = db.query(Product).order_by(Product.id.desc()).limit(3).all()
        for p in products:
            print(f"Product {p.id}: {p.name} (Status: {p.status}, Score: {p.adversary_score})")

        if not products:
            print("No products found.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
