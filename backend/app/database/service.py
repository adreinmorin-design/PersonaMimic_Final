import logging
import os

from sqlalchemy import inspect, text

# Ensure all models are registered for create_all
from app.auth.models import Role
from app.config.models import SystemSetting
from app.config.service import config_service
from app.database.database import Base, engine
from app.database.database import db_session as get_db

logger = logging.getLogger("database_service")


class DatabaseService:
    @staticmethod
    def _ensure_reverse_engineering_schema(db):
        inspector = inspect(engine)
        table_names = set(inspector.get_table_names())
        if "synthesis_jobs" not in table_names:
            return

        columns = {column["name"] for column in inspector.get_columns("synthesis_jobs")}
        required_columns = {
            "target": "target VARCHAR",
            "cluster_id": "cluster_id VARCHAR",
            "context": "context TEXT",
            "status": "status VARCHAR DEFAULT 'pending'",
            "result_code": "result_code TEXT",
            "purpose": "purpose TEXT",
            "created_at": "created_at DATETIME",
        }
        for name, ddl in required_columns.items():
            if name not in columns:
                logger.warning("[DB-MIGRATION] Adding missing column synthesis_jobs.%s", name)
                db.execute(text(f"ALTER TABLE synthesis_jobs ADD COLUMN {ddl}"))
        db.commit()

    @staticmethod
    async def init_db():
        """Initialize database tables and default data."""
        try:
            logger.info("Initializing DDD Neural Database...")
            Base.metadata.create_all(bind=engine)

            with get_db() as db:
                DatabaseService._ensure_reverse_engineering_schema(db)

                # 1. Create default roles
                roles = ["owner", "user"]
                for r_name in roles:
                    role = db.query(Role).filter(Role.name == r_name).first()
                    if not role:
                        db.add(Role(name=r_name))

                # 2. Mirror environment keys to secure DB
                env_keys = [
                    "WHOP_API_KEY",
                    "WHOP_COMPANY_ID",
                    "GUMROAD_API_KEY",
                    "BRAND_NAME",
                    "OLLAMA_CLOUD_KEY",
                    "OLLAMA_CLOUD_URL",
                ]
                for key in env_keys:
                    val = os.getenv(key)
                    if not val:
                        continue

                    existing = db.query(SystemSetting).filter(SystemSetting.key == key).first()
                    encrypted_val = config_service.encrypt(val)

                    if not existing:
                        db.add(SystemSetting(key=key, value=encrypted_val, is_encrypted=True))
                        logger.info(f"[VAULT] Mirrored {key} to system settings.")
                    elif existing.value != encrypted_val:
                        existing.value = encrypted_val
                        logger.info(f"[VAULT] Updated {key} in system settings.")

                # 3. Seed reverse-engineering target catalog
                from app.reverse_engineering.repository import reverse_engineering_repo

                await reverse_engineering_repo.seed_builtin_targets(db)

                db.commit()
                logger.info("Database initialization complete.")
        except Exception as e:
            logger.error(f"CRITICAL: Database Initialization Failed: {e}", exc_info=True)


db_service = DatabaseService()
