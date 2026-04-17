from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.schemas import CloudUpdate, ModelUpdate, SystemHealth, VaultEntry
from app.config.service import config_service
from app.database.database import get_db
from app.swarm.persona_engine import PersonaEngine

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/health", response_model=SystemHealth)
async def health(db: Session = Depends(get_db)):
    engine = PersonaEngine(config_service.get_setting(db, "model"))
    return {"status": "ok", "model": engine.model, "cloud": engine.is_cloud}


@router.get("/models")
async def get_models():
    engine = PersonaEngine()
    try:
        available_models = engine.list_available_models()
        return {"models": available_models}
    except Exception as e:
        return {"models": [f"Engine Offline: {str(e)[:50]}"]}


@router.post("", response_model=dict[str, str])
async def update_config(update: ModelUpdate, db: Session = Depends(get_db)):
    config_service.update_setting(db, "model", update.model)
    # Auto-switch persona logic
    if "fenkohq" in update.model.lower():
        config_service.update_setting(db, "persona_type", "coding")
    else:
        config_service.update_setting(db, "persona_type", "mimic")

    return {"status": "success", "model": update.model}


@router.post("/cloud", response_model=dict[str, Any])
async def update_cloud_config(update: CloudUpdate, db: Session = Depends(get_db)):
    config_service.update_setting(db, "use_cloud", str(update.use_cloud))
    return {"status": "success", "use_cloud": update.use_cloud}


@router.get("/vault")
async def get_vault(db: Session = Depends(get_db)):
    return {"settings": config_service.list_settings(db, decrypt_all=True)}


@router.post("/vault")
async def update_vault(entry: VaultEntry, db: Session = Depends(get_db)):
    config_service.update_setting(db, entry.key, entry.value, encrypt=entry.encrypt)
    return {"status": "updated", "key": entry.key}
