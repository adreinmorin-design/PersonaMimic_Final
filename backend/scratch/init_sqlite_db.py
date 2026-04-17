import os
import sys

# Ensure backend path is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.database import engine, Base
# Import all models to ensure they are registered with Base
from app.auth import models as auth_models
from app.config import models as config_models
from app.chat import models as chat_models
from app.swarm import models as swarm_models
from app.products import models as product_models
from app.reverse_engineering import models as reverse_engineering_models

print("Initializing high-fidelity SQLite database schema...")
Base.metadata.create_all(bind=engine)
print("Schema initialization COMPLETE.")
