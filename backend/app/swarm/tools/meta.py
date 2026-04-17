import os
import requests
import logging
from .base import CUSTOM_TOOL_REGISTRY, _custom_tool_module_path, _load_json_file, _save_json_file, get_current_time

logger = logging.getLogger("swarm.tools.meta")

def create_custom_tool(name: str, schema: dict, code: str):
    """Register a new custom capability."""
    try:
        path = _custom_tool_module_path(name)
        with open(path, "w", encoding="utf-8") as h: h.write(code)
        registry = _load_json_file(CUSTOM_TOOL_REGISTRY, [])
        registry = [e for e in registry if e.get("name") != name]
        registry.append({"name": name, "module": path, "schema": schema, "updated_at": get_current_time()})
        _save_json_file(CUSTOM_TOOL_REGISTRY, registry)
        return f"[META] Tool '{name}' registered."
    except Exception as e: return f"[META] Registration error: {str(e)}"

def spawn_sub_brain(name: str, model: str = "qwen2.5:7b", persona_type: str = "mimic", niche: str = ""):
    """Spawn a specialized AI brain."""
    try:
        url = "http://127.0.0.1:8055/swarm/spawn"
        requests.post(url, json={"name": name, "model": model, "persona_type": persona_type, "niche": niche}, timeout=10)
        return f"SUCCESS: Brain '{name}' spawned."
    except Exception as e: return f"Spawn error: {str(e)}"
