from pydantic import BaseModel


class ConsentRequest(BaseModel):
    username: str
    consent_given: bool
    password: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterResponse(BaseModel):
    status: str
    role: str
    username: str
    is_new_user: bool = False


class VoiceScriptResponse(BaseModel):
    status: str
    script: str


class VoiceVerifyResponse(BaseModel):
    status: str
    sentinel_key: str
    score: float
