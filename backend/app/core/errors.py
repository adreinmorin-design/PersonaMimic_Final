import logging

from fastapi.responses import JSONResponse

logger = logging.getLogger("main")


def register_exception_handlers(app):
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error("Unhandled Exception at %s: %s", request.url.path, exc, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal Server Error. The Neural Interface encountered a critical logic fault.",
                "error": str(exc),
            },
        )
