import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from sqlalchemy import text

from app.database.database import engine


def reset_sequences():
    print("[*] Synchronizing PostgreSQL Auto-Increment Sequences...")
    tables = [
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

    with engine.connect() as conn:
        for t in tables:
            try:
                # Get max id
                max_id_res = conn.execute(text(f"SELECT MAX(id) FROM {t}"))
                max_id = max_id_res.scalar() or 0

                # Check if sequence exists and update it
                seq_name = f"{t}_id_seq"
                print(f"[*] Table: {t} | Max ID: {max_id}")

                # Update sequence safely
                if max_id > 0:
                    conn.execute(text(f"SELECT setval('{seq_name}', {max_id});"))
                    print(f"    -> Sequence '{seq_name}' updated to {max_id}")

            except Exception as e:
                print(f"    [ERR] Could not update sequence for {t}: {e}")

        conn.commit()
    print("[SUCCESS] All sequences aligned.")


if __name__ == "__main__":
    reset_sequences()
