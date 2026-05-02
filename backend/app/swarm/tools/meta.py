import asyncio
import logging

import aiohttp

from .base import (
    CUSTOM_TOOL_REGISTRY,
    _custom_tool_module_path,
    _load_json_file,
    _save_json_file,
    get_current_time,
)

logger = logging.getLogger("swarm.tools.meta")


async def create_custom_tool(name: str, schema: dict, code: str):
    """Register a new custom capability."""
    try:
        path = _custom_tool_module_path(name)

        def _write():
            with open(path, "w", encoding="utf-8") as h:
                h.write(code)

        await asyncio.to_thread(_write)

        registry = await asyncio.to_thread(_load_json_file, CUSTOM_TOOL_REGISTRY, [])
        registry = [e for e in registry if e.get("name") != name]
        registry.append(
            {"name": name, "module": path, "schema": schema, "updated_at": get_current_time()}
        )
        await asyncio.to_thread(_save_json_file, CUSTOM_TOOL_REGISTRY, registry)
        return f"[META] Tool '{name}' registered."
    except Exception as e:
        return f"[META] Registration error: {str(e)}"


async def spawn_sub_brain(
    name: str, model: str = "qwen2.5:7b", persona_type: str = "mimic", niche: str = ""
):
    """Spawn a specialized AI brain."""
    try:
        url = "http://127.0.0.1:8055/swarm/spawn"
        async with aiohttp.ClientSession() as session, session.post(
            url,
            json={"name": name, "model": model, "persona_type": persona_type, "niche": niche},
            timeout=10,
        ) as response:
            if response.status == 200:
                return f"SUCCESS: Brain '{name}' spawned."
            return f"Spawn error: HTTP {response.status}"
    except Exception as e:
        return f"Spawn error: {str(e)}"
