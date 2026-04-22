import os
from contextlib import contextmanager

from dotenv import load_dotenv

# Force load environment before any SQLAlchemy initialization
print('dotenv loaded'); load_dotenv()

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.paths import DATABASE_PATH

# Standard DATABASE_URL override for cloud deployment (Postgres)
# Fallback to local SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}")

from sqlalchemy.pool import NullPool

is_sqlite = DATABASE_URL.startswith("sqlite")

if is_sqlite:
    engine_args = {
        "connect_args": {"check_same_thread": False},
        "poolclass": NullPool
    }
else:
    engine_args = {
        "pool_pre_ping": True, 
        "pool_size": 20, 
        "max_overflow": 10
    }

print('creating engine'); engine = create_engine(DATABASE_URL, **engine_args); print('engine created')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print('base created'); Base = declarative_base()


# --- SQLite Performance & Robustness Hooks ---
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if is_sqlite:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()


def get_db():
    """FastAPI Dependency: Yields a session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        try:
            db.close()
        except Exception as e:
            import logging
            logging.getLogger("database").debug(f"Failed to close db session cleanly: {e}")


db_session = contextmanager(get_db)

# Ensure all models are registered after Base is defined
print('auth models'); from app.auth import models as auth_models  # noqa
print('config models'); from app.config import models as config_models  # noqa
print('chat models'); from app.chat import models as chat_models  # noqa
print('swarm models'); from app.swarm import models as swarm_models  # noqa
print('products models'); from app.products import models as product_models  # noqa
print('reverse engineering models'); from app.reverse_engineering import models as reverse_engineering_models  # noqa
