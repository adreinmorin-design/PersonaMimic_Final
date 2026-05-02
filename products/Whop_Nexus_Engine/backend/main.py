# © 2026 Dre's Autonomous Neural Interface | Whop Nexus Engine
# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

from app.api.whop import router as whop_router

app = FastAPI(
    title="Whop Nexus Engine",
    description="Industrial Digital Product Distribution via Whop",
    version="1.0.0",
)

# CORS Configuration for Frontend Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Domain Routers
app.include_router(whop_router, prefix="/api/whop", tags=["Whop Integration"])


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Verify system operational status."""
    return {"status": "operational", "engine": "Whop Nexus v1"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
