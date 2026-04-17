import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.models import User
from app.chat.schemas import ChatRequest, ChatResponse
from app.chat.service import chat_service
from app.config.service import config_service
from app.database.database import get_db

logger = logging.getLogger("chat_router")

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Main terminal interface for human-agent interaction."""
    # 1. Identity Resolution (Default to Dre for now)
    user = db.query(User).filter(User.username == "Dre").first()
    if not user:
        raise HTTPException(status_code=403, detail="Neural identity not found.")

    # 2. Config Resolution
    system_prompt = (
        config_service.get_setting(db, "system_prompt")
        or "You are Dre's Autonomous Neural Interface."
    )
    persona_type = config_service.get_setting(db, "persona_type") or "coding"
    voice_id = config_service.get_setting(db, "voice_id")

    # 3. Execution
    try:
        response = await chat_service.execute_chat_loop(
            db=db,
            user=user,
            message=request.message,
            history=request.history,
            system_prompt=system_prompt,
            persona_type=persona_type,
            voice_id=voice_id,
        )
        return response
    except Exception as e:
        import traceback

        logger.error(f"Chat Logic Fault: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Neural Interface Fault: {str(e)}") from e
