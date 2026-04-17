import logging
import uuid

import edge_tts

from app.core.paths import STATIC_DIR

logger = logging.getLogger("voice_service")


class VoiceService:
    def __init__(self):
        # edge-tts is free and does not require an API key
        self.whisper_model = None
        # Default studio-grade voices
        self.default_voice = "en-US-AndrewNeural"

    def load_whisper(self):
        """Lazy load Whisper model."""
        if self.whisper_model:
            return
        try:
            import torch
            import whisper

            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading Whisper model (base) on {device}...")
            self.whisper_model = whisper.load_model("base", device=device)
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")

    def transcribe(self, audio_path: str) -> str:
        """STT: Audio to Text (Open Source base model)."""
        if not self.whisper_model:
            self.load_whisper()

        if not self.whisper_model:
            return "[ERROR] Whisper engine offline."

        try:
            import torch

            result = self.whisper_model.transcribe(audio_path, fp16=torch.cuda.is_available())
            return result.get("text", "").strip()
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return f"[ERROR] Transcription failed: {e}"

    async def text_to_speech(self, text: str, voice: str | None = None) -> str | None:
        """TTS: Text to Audio URL using free Edge-TTS neural voices."""
        try:
            output_filename = f"mimic_{uuid.uuid4()}.mp3"
            output_path = STATIC_DIR / output_filename

            selected_voice = voice or self.default_voice

            communicate = edge_tts.Communicate(text, selected_voice)
            await communicate.save(str(output_path))

            logger.info(f"TTS Success: {output_filename} (Voice: {selected_voice})")
            return f"/static/{output_filename}"
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None

    async def list_voices(self):
        """Returns list of available free neural voices."""
        try:
            voices = await edge_tts.VoicesManager.create()
            return voices.find(Locale="en-US")
        except Exception as e:
            logger.error(f"Voice list error: {e}")
            return []


voice_service = VoiceService()
