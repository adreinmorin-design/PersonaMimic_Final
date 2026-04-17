from pydantic import BaseModel


class SwarmSpawnRequest(BaseModel):
    name: str
    model: str = "qwen2.5:7b"
    persona_type: str = "coding"
    niche: str = ""


class SwarmDirectiveRequest(BaseModel):
    directive: str | None = None


class SwarmStatus(BaseModel):
    running: bool
    tasks_completed: int
    log: list


class AdversaryRequest(BaseModel):
    product_name: str = "product"
