from pydantic import BaseModel


class ConsentRequest(BaseModel):
    username: str
    consent_given: bool


class RegisterResponse(BaseModel):
    status: str
    role: str
    username: str


class VoiceScriptResponse(BaseModel):
    status: str
    script: str


class VoiceVerifyResponse(BaseModel):
    status: str
    sentinel_key: str
    score: float
