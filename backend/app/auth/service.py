import asyncio
import logging
import os
from typing import Any

import aiofiles
import torch
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.repository import auth_repo
from app.auth.schemas import ConsentRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger("auth_service")

try:
    import torchaudio
    import torchaudio.transforms as transforms
except ImportError:
    torchaudio = None

logger = logging.getLogger("auth_service")

# Static configuration
MASTER_VOICE_FILE = os.path.abspath(os.path.join(os.getcwd(), "app", "auth", "master_voice.wav"))
MODEL_SOURCE = "speechbrain/spkrec-ecapa-voxceleb"
SAVEDIR = os.path.abspath(os.path.join(os.getcwd(), "tmpdir_speechbrain"))
DEFAULT_VOICE_TRAINING_SCRIPT = (
    "My voice is my password. PersonaMimic recognizes me as the secure operator of this studio."
)


class AuthService:
    def __init__(self):
        self.verifier = None
        self.is_loading = False

    def load_model(self):
        """Lazy load the model to avoid blocking FastAPI startup."""
        if self.verifier or self.is_loading:
            return
        self.is_loading = True
        try:
            from speechbrain.inference.speaker import SpeakerRecognition

            logger.info(f"Downloading/Loading SpeechBrain model from {MODEL_SOURCE}...")
            self.verifier = SpeakerRecognition.from_hparams(source=MODEL_SOURCE, savedir=SAVEDIR)
            logger.info("SpeechBrain model loaded securely.")
        except Exception as e:
            logger.error(f"Failed to initialize VoiceAuthenticator: {e}")
        finally:
            self.is_loading = False

    def has_master_voice(self) -> bool:
        return os.path.exists(MASTER_VOICE_FILE)

    def preprocess_audio(self, wav_path: str) -> bool:
        """Robustly checks, converts to mono 16kHz, normalizes, and filters silent/short audio."""
        if torchaudio is None:
            logger.warning("torchaudio not installed, skipping robust preprocessing.")
            return True

        try:
            waveform, sample_rate = torchaudio.load(wav_path)

            # Convert to mono
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)

            # Resample to 16kHz
            if sample_rate != 16000:
                resampler = transforms.Resample(orig_freq=sample_rate, new_freq=16000)
                waveform = resampler(waveform)

            # Volume Normalization
            waveform = waveform - waveform.mean()
            max_val = waveform.abs().max()

            # Check length (must be > 1.5 seconds) and non-silent
            if waveform.shape[1] < 16000 * 1.5:
                logger.error("Audio rejected: Too short (< 1.5s).")
                return False

            if max_val < 0.01:
                logger.error("Audio rejected: Too quiet/silent.")
                return False

            # Normalize peak to 0.9
            waveform = waveform / max_val * 0.9

            # Save processed audio back
            torchaudio.save(wav_path, waveform, 16000)
            return True
        except Exception as e:
            logger.error(f"Preprocessing audio failed: {e}")
            return False

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def register_user(self, db: Session, request: ConsentRequest) -> User:
        """Register a new user and assign roles."""
        is_first = auth_repo.get_user_count(db) == 0
        # Dre is always owner, regardless of order
        role_name = "owner" if is_first or request.username.lower() == "dre" else "user"

        user = auth_repo.get_user_by_username(db, request.username)
        if not user:
            role = auth_repo.get_role_by_name(db, role_name)
            if not role:
                logger.info(f"Role '{role_name}' not found. Creating autonomously.")
                role = auth_repo.create_role(db, role_name)
                if role_name == "owner":
                    auth_repo.create_role(db, "user")

            hashed = self.get_password_hash(request.password) if request.password else None
            user = auth_repo.create_user(db, request.username, role.id, hashed)
        else:
            # Enforce Dre as owner even if already exists as user
            if request.username.lower() == "dre":
                owner_role = auth_repo.get_role_by_name(db, "owner")
                if user.role_id != owner_role.id:
                    user.role_id = owner_role.id
                    db.commit()
                    db.refresh(user)

        return user

    def login(self, db: Session, request: Any) -> User:
        user = auth_repo.get_user_by_username(db, request.username)
        if not user:
            raise ValueError("User not found.")

        if user.hashed_password:
            if not self.verify_password(request.password, user.hashed_password):
                raise ValueError("Invalid password.")
        elif request.username.lower() == "dre":
            # First time Dre logins, they set their password
            hashed = self.get_password_hash(request.password)
            auth_repo.update_user_password(db, user, hashed)
            logger.info("Master Operator 'Dre' has set their secure password.")

        return user

    def auto_onboard(self, db: Session):
        """Zero-guidance initialization: ensure a default owner exists."""
        if auth_repo.get_user_count(db) > 0:
            return

        logger.info("[ONBOARDING] No users found. Initializing Master Operator 'Dre'...")
        owner_role = auth_repo.get_role_by_name(db, "owner")
        if not owner_role:
            owner_role = auth_repo.create_role(db, "owner")
            auth_repo.create_role(db, "user")

        auth_repo.create_user(db, "Dre", owner_role.id)
        logger.info("[ONBOARDING] Master Operator 'Dre' initialized autonomously.")

    async def register_auth_voice(self, temp_wav_path: str, username: str) -> bool:
        """Process and save the master voice print."""
        try:
            if not self.preprocess_audio(temp_wav_path):
                return False

            os.makedirs(os.path.dirname(MASTER_VOICE_FILE), exist_ok=True)
            async with aiofiles.open(temp_wav_path, "rb") as src:
                payload = await src.read()
            async with aiofiles.open(MASTER_VOICE_FILE, "wb") as dst:
                await dst.write(payload)

            # Trigger lazy loading of model if needed
            asyncio.create_task(asyncio.to_thread(self.load_model))
            return True
        except Exception as e:
            logger.error(f"Voice registration error: {e}")
            return False

    def get_voice_training_script(self) -> str:
        return DEFAULT_VOICE_TRAINING_SCRIPT

    def verify_voice(self, attempt_wav_path: str) -> dict[str, Any]:
        """Verify an incoming voice against the master print."""
        if not self.verifier:
            self.load_model()
            if not self.verifier:
                return {"error": "Voice biometric engine offline", "success": False, "match": False}

        if not self.has_master_voice():
            return {"error": "No master voice print found", "success": False, "match": False}

        try:
            if not self.preprocess_audio(attempt_wav_path):
                return {"error": "Audio validation failed", "success": False, "match": False}

            score, prediction = self.verifier.verify_files(MASTER_VOICE_FILE, attempt_wav_path)
            match_status = bool(prediction.item())
            confidence = float(score.item())

            return {"success": True, "match": match_status, "score": confidence}
        except Exception as e:
            logger.error(f"Voice verification error: {e}")
            return {"error": str(e), "success": False, "match": False}


auth_service = AuthService()
