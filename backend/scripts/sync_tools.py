import json
import sqlite3
from pathlib import Path

# Setup paths
BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
DATABASE_PATH = PROJECT_ROOT / "persona_mimic.db"
CUSTOM_TOOLS_DIR = BACKEND_DIR / "custom_tools"
REGISTRY_PATH = CUSTOM_TOOLS_DIR / "tool_registry.json"

CUSTOM_TOOLS_DIR.mkdir(exist_ok=True)


def slugify(text):
    import re

    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def sync_tools():
    if not DATABASE_PATH.exists():
        print(f"Database not found at {DATABASE_PATH}")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Get all completed replicated tools, ordered by ID desc so we get the latest versions first
    cursor.execute(
        "SELECT id, tool_name, purpose_summary, replicated_code FROM replicated_tools WHERE status = 'completed' ORDER BY id DESC"
    )
    tools = cursor.fetchall()

    if not tools:
        print("No completed tools found to sync.")
        return

    # Load registry
    registry = []
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH) as f:
            registry = json.load(f)

    processed_slugs = set()
    for tool_id, name, purpose, code in tools:
        slug = slugify(name)
        if not slug:
            slug = f"tool_{tool_id}"

        if slug in processed_slugs:
            continue
        processed_slugs.add(slug)

        file_path = CUSTOM_TOOLS_DIR / f"{slug}.py"

        # Write code
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        # Update registry
        entry = {
            "name": slug,
            "display_name": name,
            "purpose": purpose,
            "module": str(file_path),
            "schema": {
                "type": "object",
                "properties": {
                    "task_context": {
                        "type": "string",
                        "description": "Context for the tool execution",
                    }
                },
                "required": ["task_context"],
            },
        }

        # Replace if exists
        registry = [e for e in registry if e.get("name") != slug]
        registry.append(entry)
        print(f"Synced tool: {name} -> {slug}.py")

    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)

    conn.close()
    print(f"Sync complete. {len(processed_slugs)} unique tools registered.")


if __name__ == "__main__":
    sync_tools()
