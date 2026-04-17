import os
from contextlib import contextmanager

from dotenv import load_dotenv

# Force load environment before any SQLAlchemy initialization
load_dotenv()

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.paths import DATABASE_PATH

# Standard DATABASE_URL override for cloud deployment (Postgres)
# Fallback to local SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}")

is_sqlite = DATABASE_URL.startswith("sqlite")

engine_args = {"pool_pre_ping": True}
if is_sqlite:
    engine_args["connect_args"] = {"check_same_thread": False}

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
        db.close()


db_session = contextmanager(get_db)

# Ensure all models are registered after Base is defined
from app.auth import models as auth_models  # noqa
from app.config import models as config_models  # noqa
from app.chat import models as chat_models  # noqa
from app.swarm import models as swarm_models  # noqa
from app.products import models as product_models  # noqa
from app.reverse_engineering import models as reverse_engineering_models  # noqa
