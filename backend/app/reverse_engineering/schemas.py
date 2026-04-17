from datetime import datetime

from pydantic import BaseModel, Field


class SynthesisRequest(BaseModel):
    target: str
    cluster_id: str
    context: str
    purpose: str | None = None


class SynthesisResponse(BaseModel):
    id: int
    target: str
    status: str
    result_code: str | None = None
    purpose: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class AgentTargetCreateRequest(BaseModel):
    target_id: str = Field(min_length=2, max_length=100)
    name: str = Field(min_length=2, max_length=200)
    description: str | None = None
    source_repo_url: str | None = None
    aliases: list[str] = Field(default_factory=list)


class AgentTargetResponse(BaseModel):
    id: int
    target_id: str
    name: str
    description: str | None = None
    source_repo_url: str | None = None
    aliases: list[str] = Field(default_factory=list)
    is_builtin: bool
    created_at: datetime


class ReplicatedToolResponse(BaseModel):
    id: int
    job_id: int
    target_id: str
    target_name: str
    tool_name: str
    source_repo_url: str | None = None
    status: str
    purpose_summary: str | None = None
    explanation: str | None = None
    prerequisites: list[str] = Field(default_factory=list)
    setup_steps: list[str] = Field(default_factory=list)
    run_steps: list[str] = Field(default_factory=list)
    integration_steps: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    replicated_code: str | None = None
    created_at: datetime
