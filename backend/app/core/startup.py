import asyncio
import logging
import os

from app.core.ollama_utils import ensure_ollama_started, ensure_required_models
from app.database.service import db_service
from app.swarm.service import swarm_manager

logger = logging.getLogger("main")
DEFAULT_STARTUP_NICHE = "Trending High-Yield Digital Assets"
REQUIRED_MODELS = ["qwen2.5-coder:7b", "qwen2.5-coder:7b"]


async def initialize_llm():
    """Ensure LLM engine is ready before starting brains."""
    success = await ensure_ollama_started()
    if success:
        # Avoid blocking startup too long, but ensure models are present
        asyncio.create_task(ensure_required_models(REQUIRED_MODELS))
    else:
        logger.error(
            "[STARTUP] LLM Engine (Ollama) failed to initialize. Brains may be non-functional."
        )


async def initialize_swarm():
    await initialize_llm()
    await db_service.init_db()
    await swarm_manager.initialize()

    # Autonomous Onboarding (Full Autonomy Phase 1)
    from app.auth.service import auth_service
    from app.database.database import SessionLocal

    db = SessionLocal()
    try:
        auth_service.auto_onboard(db)
    finally:
        db.close()

    autostart_env = os.getenv("SWARM_AUTOSTART", "true").strip().lower()
    autostart_enabled = autostart_env in {"1", "true", "yes", "on"}
    if not autostart_enabled:
        logger.info("[STARTUP] Swarm auto-start disabled via SWARM_AUTOSTART.")
        return

    for index, (name, brain) in enumerate(swarm_manager.brains.items()):
        if index > 0:
            logger.info("[STARTUP] Staggering '%s' initiation (5s delay)...", name)
            await asyncio.sleep(5)

        logger.info("[STARTUP] Launching brain '%s' in autonomous mode...", name)
        try:
            brain.start(niche=DEFAULT_STARTUP_NICHE)
        except Exception as exc:
            logger.error("[STARTUP] Failed to launch brain '%s': %s", name, exc, exc_info=True)


def register_startup_events(app):
    @app.on_event("startup")
    async def startup_event():
        await initialize_swarm()
