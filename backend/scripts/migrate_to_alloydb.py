import os
import sys

from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine, select
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.database import DATABASE_PATH, Base


def migrate():
    load_dotenv()

    sqlite_url = f"sqlite:///{DATABASE_PATH.as_posix()}"
    postgres_url = os.getenv("DATABASE_URL")

    if not postgres_url or "sqlite" in postgres_url:
        print("\n[!] ERROR: DATABASE_URL is not set to a PostgreSQL/AlloyDB instance.")
        print("Please update your .env file with the following format:")
        print("DATABASE_URL=postgresql://user:password@host:5432/dbname")
        return

    print("\n[*] Starting Industrial Migration...")
    print(f"[*] Source: {sqlite_url}")
    print(f"[*] Target: {postgres_url}")

    source_engine = create_engine(sqlite_url)
    target_engine = create_engine(postgres_url)

    # 1. Create tables on target
    print("\n[*] Synchronizing table schemas on AlloyDB...")
    # Import all models to ensure they are registered with Base

    try:
        Base.metadata.create_all(target_engine)
        print("[OK] Target schema is now synchronized.")
    except Exception as e:
        print(f"[ERR] Schema creation failed: {e}")
        return

    # 2. Reflect tables to migrate data
    source_meta = MetaData()
    source_meta.reflect(bind=source_engine)

    target_meta = MetaData()
    target_meta.reflect(bind=target_engine)

    SourceSession = sessionmaker(bind=source_engine)
    TargetSession = sessionmaker(bind=target_engine)

    source_session = SourceSession()
    target_session = TargetSession()

    try:
        # Tables to migrate in dependency order
        # Role first, then User, then things depending on User.
        table_names = [
            "roles",
            "users",
            "interaction_logs",
            "system_settings",
            "keystrokes",
            "task_queue",
            "review_pool",
            "task_board",
            "products",
        ]

        for name in table_names:
            if name not in source_meta.tables:
                continue

            source_table = source_meta.tables[name]
            target_table = target_meta.tables[name]

            print(f"[*] Migrating table: {name}...")

            # Fetch all rows from source
            rows = source_session.execute(select(source_table)).all()
            if not rows:
                print("    -> Table is empty. Skipping.")
                continue

            # Convert to dicts for insertion
            data = [dict(row._mapping) for row in rows]

            # Clean insertion into target
            # Note: We skip rows that already exist by checking the ID (if present)
            # or just catching the exception per row for simplicity in this utility
            for row_data in data:
                try:
                    target_session.execute(target_table.insert(), row_data)
                    target_session.commit()
                except Exception:
                    target_session.rollback()
                    # logger.debug(f"Skipping duplicate in {name}")
                    continue

            print(f"    [OK] Migration sweep complete for {name}.")

        print("\n[*] Finalizing transaction...")
        target_session.commit()
        print("[SUCCESS] All local data pushed to AlloyDB.")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Data migration aborted: {e}")
        target_session.rollback()
    finally:
        source_session.close()
        target_session.close()


if __name__ == "__main__":
    migrate()
