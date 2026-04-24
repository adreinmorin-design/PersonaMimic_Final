from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.auth.router import router as auth_router
from app.chat.router import router as chat_router
from app.config.router import router as config_router
from app.core.errors import register_exception_handlers
from app.core.middleware import configure_middleware
from app.core.observability import setup_observability
from app.core.paths import STATIC_DIR
from app.core.startup import register_startup_events
from app.forge.router import router as forge_router
from app.products.router import router as product_router
from app.reverse_engineering.router import router as reverse_engineering_router
from app.swarm.router import router as swarm_router
from app.system.router import router as system_router
from app.voice.router import router as voice_router
from app.n8n.router import router as n8n_router


def create_app() -> FastAPI:
    app = FastAPI(title="PersonaMimic AI Neural Interface", version="2.0.0")

    setup_observability(app)
    configure_middleware(app)
    register_exception_handlers(app)
    register_startup_events(app)

    app.include_router(auth_router)
    app.include_router(swarm_router)
    app.include_router(chat_router)
    app.include_router(voice_router)
    app.include_router(config_router)
    app.include_router(product_router)
    app.include_router(forge_router)
    app.include_router(reverse_engineering_router)
    app.include_router(system_router)
    app.include_router(n8n_router)

    @app.get("/")
    async def index():
        return {
            "status": "online",
            "message": "PersonaMimic AI Neural API is Active.",
            "version": "2.0.0",
        }

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app
