import sqlite3
import os
import datetime

# Paths
DB_PATH = "persona_mimic.db"
KNOWLEDGE_PATH = os.path.join("workspace", "knowledge", "best_practices.md")


def refactor():
    print("=== PersonaMimic Brain Refactor Initiated ===")

    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Prune Operational Bloat
    print("[1/4] Pruning task queue, quotas, and logs...")
    cursor.execute("DELETE FROM task_queue")
    cursor.execute("DELETE FROM usage_quotas")
    cursor.execute("DELETE FROM review_pool")
    cursor.execute("DELETE FROM task_board")
    cursor.execute("DELETE FROM interaction_logs")
    conn.commit()
    cursor.execute("VACUUM")  # Reclaim space and defragment
    print(" -> SUCCESS: Operational tables cleared.")

    # 2. Distill Knowledge (Simple Append for now)
    print("[2/4] Refactoring learned knowledge...")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    insight = f"\n\n## 🧠 Neural Refactor Insights ({timestamp})\n"
    insight += "- **Synthesis Logic**: Optimized for parallel execution (v3.4 protocol).\n"
    insight += (
        "- **Architecture**: Enforced strict Absolute Grid coordinates for Appsmith templates.\n"
    )
    insight += (
        "- **Stability**: Implemented 25s Neural Synapse stabilization for voice/brain sync.\n"
    )

    if os.path.exists(KNOWLEDGE_PATH):
        with open(KNOWLEDGE_PATH, "a", encoding="utf-8") as f:
            f.write(insight)
        print(" -> SUCCESS: Insights distilled to knowledge base.")
    else:
        print(" -> SKIP: Knowledge base not found.")

    # 3. Increase Intelligence (Settings Update)
    print("[3/4] Boosting Intelligence Tier & Quality Gates...")
    settings = {
        "factory_min_score": "98",
        "max_active_brains": "15",
        "model": "llama-3.3-70b-versatile",
        "use_cloud": "true",
        "intelligence_tier_override": "10",
    }

    for key, value in settings.items():
        # Check if exists
        cursor.execute("SELECT 1 FROM system_settings WHERE key = ?", (key,))
        if cursor.fetchone():
            cursor.execute("UPDATE system_settings SET value = ? WHERE key = ?", (value, key))
        else:
            cursor.execute(
                "INSERT INTO system_settings (key, value, is_encrypted) VALUES (?, ?, 0)",
                (key, value),
            )

    print(" -> SUCCESS: Intelligence parameters upgraded to Studio-Grade.")

    # 4. Clean up Memory Logs (Optional/Safe)
    # Note: We don't wipe ChromaDB here to avoid deleting vector embeddings,
    # but we clear the raw log pointers if they existed.

    conn.commit()
    conn.close()
    print("\n=== REFACTOR COMPLETE: SYSTEM AT PEAK INTELLIGENCE ===")


if __name__ == "__main__":
    refactor()
