from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.auth.service import auth_service
from app.chat.service import chat_service
from app.config.service import config_service
from app.core.uploads import uploaded_file
from app.database.database import get_db
from app.voice.service import voice_service

router = APIRouter(prefix="/voice", tags=["voice"])


@router.get("/list")
async def list_available_voices():
    """List available free neural voices."""
    voices = await voice_service.list_voices()
    return {
        "voices": [
            {"name": v["FriendlyName"], "id": v["ShortName"], "gender": v["Gender"]} for v in voices
        ]
    }


@router.post("/autonomous-chat")
async def autonomous_voice_chat(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    NEURAL AUTO-PROCESSOR:
    Biometric Gate -> Whisper STT -> LLM Engine -> Edge-TTS.
    """
    async with uploaded_file(file, prefix="auto") as temp_path:
        # 1. Biometric Gate (Open Source Verification)
        bio_result = auth_service.verify_voice(temp_path)
        if not bio_result.get("success") or not bio_result.get("match"):
            return {"status": "ignored", "reason": "Biometric mismatch"}

        # 2. Local Whisper Transcription
        transcript = voice_service.transcribe(temp_path)
        if not transcript or transcript.startswith("[ERROR]"):
            return {"status": "ignored", "reason": "Transcription failed"}

        # 3. Agentic Processing Loop
        system_prompt = config_service.get_setting(db, "system_prompt")
        persona_type = config_service.get_setting(db, "persona_type") or "mimic"
        voice_id = config_service.get_setting(db, "voice_id") or "en-US-AndrewNeural"

        response_data = await chat_service.execute_chat_loop(
            db=db,
            user=None,  # System-level trigger
            message=transcript,
            history=[],
            system_prompt=system_prompt,
            persona_type=persona_type,
            voice_id=voice_id,
        )

        return {
            "status": "success",
            "text": transcript,
            "response": response_data.response,
            "audio_url": response_data.audio_url,
        }
