import asyncio
import logging
import os
import urllib.request

logger = logging.getLogger("ollama_utils")

OLLAMA_PORT = 11434
OLLAMA_URL = f"http://127.0.0.1:{OLLAMA_PORT}"


def _ping_ollama() -> bool:
    """Synchronous ping for use with asyncio.to_thread."""
    try:
        with urllib.request.urlopen(OLLAMA_URL, timeout=1) as response:
            return response.status == 200
    except Exception:
        return False


async def is_ollama_running() -> bool:
    """Check if Ollama service is reachable."""
    return await asyncio.to_thread(_ping_ollama)


async def ensure_ollama_started():
    """Ensure Ollama is running, start it if not."""
    if await is_ollama_running():
        logger.info("[OLLAMA] Service already online.")
        return True

    logger.warning("[OLLAMA] Service offline. Attempting automated startup...")
    try:
        # Start Ollama service in the background
        creation_flags = 0
        if os.name == "nt":
            creation_flags = 0x08000000  # CREATE_NO_WINDOW

        await asyncio.create_subprocess_exec(
            "ollama",
            "serve",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
            creationflags=creation_flags,
        )

        # Wait and verify
        for attempt in range(10):
            await asyncio.sleep(2)
            if await is_ollama_running():
                logger.info("[OLLAMA] Service verified ONLINE.")
                return True
            logger.debug("[OLLAMA] Waiting for service (attempt %d/10)...", attempt + 1)

    except FileNotFoundError:
        logger.error("[OLLAMA] Executable 'ollama' not found in PATH.")
    except Exception as e:
        logger.error("[OLLAMA] Failed to start service: %s", e)

    return False


async def ensure_required_models(models: list[str]):
    """Ensure specific models are available in Ollama."""
    if not await is_ollama_running():
        logger.error("[OLLAMA] Cannot check models: service offline.")
        return

    for model in models:
        try:
            # Check if model exists
            process = await asyncio.create_subprocess_exec(
                "ollama", "list", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            if model not in stdout.decode():
                logger.warning("[OLLAMA] Model '%s' missing. Pulling...", model)
                pull_proc = await asyncio.create_subprocess_exec("ollama", "pull", model)
                await pull_proc.wait()
                logger.info("[OLLAMA] Model '%s' successfully pulled.", model)
            else:
                logger.debug("[OLLAMA] Model '%s' verified.", model)
        except Exception as e:
            logger.error("[OLLAMA] Failed to verify/pull model '%s': %s", model, e)
