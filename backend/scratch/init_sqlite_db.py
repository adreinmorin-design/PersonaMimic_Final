import os
import sys

# Ensure backend path is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.database import Base, engine

# Import all models to ensure they are registered with Base

print("Initializing high-fidelity SQLite database schema...")
Base.metadata.create_all(bind=engine)
print("Schema initialization COMPLETE.")
