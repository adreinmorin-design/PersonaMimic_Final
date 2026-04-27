import os
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.schemas import CloudUpdate, ModelUpdate, SystemHealth, VaultEntry
from app.config.service import config_service
from app.database.database import get_db
from app.swarm.persona_engine import MODEL_FALLBACK, PersonaEngine

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/health", response_model=SystemHealth)
async def health(db: Session = Depends(get_db)):
    model = config_service.get_setting(db, "model") or os.getenv("CURRENT_MODEL") or MODEL_FALLBACK
    db_use_cloud = config_service.get_setting(db, "use_cloud")
    env_use_cloud = os.getenv("USE_CLOUD", "false").strip().lower() == "true"
    use_cloud = (
        str(db_use_cloud).strip().lower() == "true" if db_use_cloud is not None else False
    ) or env_use_cloud
    return {"status": "ok", "model": model, "cloud": use_cloud}


@router.get("/models")
async def get_models():
    engine = PersonaEngine()
    try:
        available_models = await engine.list_available_models()
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

    PersonaEngine.clear_caches()
    return {"status": "success", "model": update.model}


@router.post("/cloud", response_model=dict[str, Any])
async def update_cloud_config(update: CloudUpdate, db: Session = Depends(get_db)):
    config_service.update_setting(db, "use_cloud", str(update.use_cloud))
    PersonaEngine.clear_caches()
    return {"status": "success", "use_cloud": update.use_cloud}


@router.get("/vault")
async def get_vault(db: Session = Depends(get_db)):
    return {"settings": config_service.list_settings(db, decrypt_all=True)}


@router.post("/vault")
async def update_vault(entry: VaultEntry, db: Session = Depends(get_db)):
    config_service.update_setting(db, entry.key, entry.value, encrypt=entry.encrypt)
    return {"status": "updated", "key": entry.key}
