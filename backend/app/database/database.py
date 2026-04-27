import os
from contextlib import contextmanager
import logging

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.paths import DATABASE_PATH

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}")

is_sqlite = DATABASE_URL.startswith("sqlite")
logger = logging.getLogger("database")

if is_sqlite:
    engine_args = {
        "connect_args": {"check_same_thread": False},
    }
else:
    engine_args = {
        "pool_pre_ping": True,
        "pool_size": 20,
        "max_overflow": 10,
    }

engine = create_engine(DATABASE_URL, **engine_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


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
            logger.debug("Failed to close db session cleanly: %s", e)


db_session = contextmanager(get_db)

# Ensure all models are registered after Base is defined
from app.auth import models as auth_models  # noqa
from app.chat import models as chat_models  # noqa
from app.config import models as config_models  # noqa
from app.products import models as product_models  # noqa
from app.reverse_engineering import models as reverse_engineering_models  # noqa
from app.swarm import models as swarm_models  # noqa
