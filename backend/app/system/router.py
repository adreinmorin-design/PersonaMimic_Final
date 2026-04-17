from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.system.service import system_service

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/intelligence")
def get_intelligence(db: Session = Depends(get_db)):
    """Returns the current intelligence tier and active capabilities."""
    return system_service.get_intelligence(db)


@router.get("/health")
def get_health():
    """Returns the health status of core industrial subsystems."""
    return system_service.get_health()
