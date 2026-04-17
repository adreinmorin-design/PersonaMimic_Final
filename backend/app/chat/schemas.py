from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str
    audio_url: str | None = None
    logs: list[dict] = Field(default_factory=list)
    files: list[str] = Field(default_factory=list)
    role: str
