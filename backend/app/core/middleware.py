import os

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

PUBLIC_PATH_PREFIXES = (
    "/",
    "/static",
    "/auth/register",
    "/auth/voice-register",
    "/auth/voice-verify",
    "/voice/autonomous-chat",
    "/config/health",
)
SECURITY_KEY = os.getenv("SECURITY_KEY", "dre_secure_2026")


def configure_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def sentinel_lockdown(request, call_next):
        if any(request.url.path.startswith(path) for path in PUBLIC_PATH_PREFIXES):
            return await call_next(request)

        auth_key = request.headers.get("X-Security-Key")
        if auth_key != SECURITY_KEY:
            return JSONResponse(
                status_code=403,
                content={"detail": "SENTINEL BLOCK: Unauthorized Access Attempt."},
            )

        return await call_next(request)
