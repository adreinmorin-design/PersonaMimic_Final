import datetime
import json
import logging
import os
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [NODEMANAGER] %(message)s")
logger = logging.getLogger("codesmith_node_manager")


def _registry_path() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "node_registry.json")


def _load_registry(path: str) -> list[dict[str, Any]]:
    if not os.path.exists(path):
        return []

    try:
        with open(path, encoding="utf-8") as handle:
            payload = json.load(handle)
        return payload if isinstance(payload, list) else []
    except Exception as exc:
        logger.warning("Registry read failed, rebuilding registry file: %s", exc)
        return []


def _save_registry(path: str, payload: list[dict[str, Any]]) -> None:
    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    os.replace(temp_path, path)


def manage_node(
    node_name: str,
    node_type: str,
    status: str = "ACTIVE",
    load: Any = 0.15,
    capabilities: list[str] | None = None,
    message: str | None = None,
) -> str:
    """
    Industrial Node Manager for the Codesmith Cluster.
    Orchestrates specialized sub-nodes for asset production and persists their status.
    """
    registry_path = _registry_path()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    capabilities = capabilities or ["code_generation", "refactoring", "unit_testing"]
    status_text = (status or "ACTIVE").upper()
    load_text = (
        f"{float(load):.2f}"
        if isinstance(load, (int, float)) or str(load).replace(".", "", 1).isdigit()
        else str(load)
    )

    node_status = {
        "node_name": node_name,
        "node_type": node_type,
        "status": status_text,
        "last_sync": timestamp,
        "load": load_text,
        "capabilities": capabilities,
        "message": message
        or f"Codesmith Node '{node_name}' ({node_type}) is now synchronized and reporting to the Hive-Mind.",
    }

    try:
        registry = _load_registry(registry_path)
        updated = False
        for index, entry in enumerate(registry):
            if entry.get("node_name") == node_name:
                registry[index] = node_status
                updated = True
                break

        if not updated:
            registry.append(node_status)

        registry.sort(key=lambda entry: entry.get("node_name", ""))
        _save_registry(registry_path, registry)

        logger.info("Successfully registered node '%s' in the hive-mind registry.", node_name)
        return json.dumps(node_status)
    except Exception as exc:
        logger.error("Node Manager Failure: %s", exc)
        return json.dumps({"status": "ERROR", "message": f"Manager failed: {exc}"})


def codesmith_node_manager(
    node_name: str,
    node_type: str,
    status: str = "ACTIVE",
    load: Any = 0.15,
    capabilities: list[str] | None = None,
    message: str | None = None,
) -> str:
    """Custom-tool entrypoint matching the registered tool name."""
    return manage_node(
        node_name=node_name,
        node_type=node_type,
        status=status,
        load=load,
        capabilities=capabilities,
        message=message,
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 2:
        print(manage_node(sys.argv[1], sys.argv[2]))
    else:
        print(manage_node("Codesmith-Alpha", "LeadEngine"))
