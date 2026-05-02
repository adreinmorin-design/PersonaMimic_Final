import datetime
import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth.schemas import (
    ConsentRequest,
    LoginRequest,
    RegisterResponse,
    VoiceScriptResponse,
    VoiceVerifyResponse,
)
from app.auth.service import auth_service
from app.core.uploads import uploaded_file
from app.database.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse)
async def register(request: ConsentRequest, db: Session = Depends(get_db)):
    print(f"[DEBUG-AUTH] Registration attempt for: {request.username}")
    if not request.consent_given:
        print("[DEBUG-AUTH] Consent missing")
        raise HTTPException(status_code=400, detail="Consent is mandatory.")

    try:
        user = auth_service.register_user(db, request)
        print(f"[DEBUG-AUTH] Registration successful for: {user.username}")
        return {
            "status": "success",
            "role": user.role.name if user.role else "user",
            "username": user.username,
            "is_new_user": True,
        }
    except Exception as e:
        import traceback

        with open("auth_debug.log", "a") as f:
            f.write(f"\n--- Registration Error at {datetime.datetime.now()} ---\n")
            traceback.print_exc(file=f)
        print(f"[DEBUG-AUTH] Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=RegisterResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = auth_service.login(db, request)
        return {
            "status": "success",
            "role": user.role.name if user.role else "user",
            "username": user.username,
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice-register")
async def register_auth_voice(file: UploadFile = File(...), username: str = "Dre"):
    async with uploaded_file(file, prefix="master") as temp_path:
        success = await auth_service.register_auth_voice(temp_path, username)

    if not success:
        raise HTTPException(status_code=500, detail="Voice biometric engine failure")

    return {"status": "success", "message": "Voice Print Encrypted"}


@router.get("/voice-scripts", response_model=VoiceScriptResponse)
async def get_voice_script():
    return {"status": "success", "script": auth_service.get_voice_training_script()}


@router.post("/voice-verify", response_model=VoiceVerifyResponse)
async def verify_auth_voice(file: UploadFile = File(...)):
    async with uploaded_file(file, prefix="verify") as temp_path:
        result = auth_service.verify_voice(temp_path)
        if result.get("success") and result.get("match"):
            # Provide security key from environment (sentinel)
            security_key = os.getenv("SECURITY_KEY", "dre_secure_2026")
            return {"status": "success", "sentinel_key": security_key, "score": result.get("score")}
        elif not result.get("success"):
            raise HTTPException(
                status_code=500, detail=result.get("error", "Error loading voice model")
            )
        else:
            raise HTTPException(
                status_code=403, detail="Voice Biometric Mis-Match. Intruder Blocked."
            )
