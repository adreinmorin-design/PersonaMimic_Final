from typing import Any

from pydantic import BaseModel, Field


class FileManagerArgs(BaseModel):
    action: str = Field(..., pattern="^(write|append|read|list|delete|replace)$")
    filename: str | None = None
    content: str | None = None
    target: str | None = None
    replacement: str | None = None


class SearchArgs(BaseModel):
    query: str


class ValidationArgs(BaseModel):
    product_name: str
    files: list[str] | None = None


class PackageArgs(BaseModel):
    product_name: str
    files: list[str] | None = None


class LaunchArgs(BaseModel):
    platform: str
    product_name: str


class SpawnArgs(BaseModel):
    name: str
    model: str = "qwen2.5:7b"
    persona_type: str = "coding"
    niche: str = ""


class EcommerceArgs(BaseModel):
    platform: str
    api_key: str | None = None
    title: str
    description: str
    price: float
    currency: str = "USD"
    company_id: str | None = None


class PeerReviewArgs(BaseModel):
    product_name: str
    reviewer_brain: str = "Unknown"
    status: str = Field(..., pattern="^(approved|rejected|correction_needed)$")
    critique: str


class SelfHealArgs(BaseModel):
    traceback: str
    context: str


class SocialMarketingArgs(BaseModel):
    platform: str = Field(..., pattern="^(twitter|x|linkedin)$")
    content: str


class SaaSArchitectArgs(BaseModel):
    product_name: str
    stack: str = "fastapi-react"
    features: list[str]


class AffiliateResearchArgs(BaseModel):
    niche: str
    min_commission: float = 20.0


class MarketingCopyArgs(BaseModel):
    product_name: str
    niche: str


class WhopAppArgs(BaseModel):
    product_name: str
    niche: str


class VisualsArgs(BaseModel):
    product_name: str
    description: str


class AssembleArgs(BaseModel):
    product_name: str
    niche: str | None = ""
    is_app: bool = False


class PredictiveOutcomeArgs(BaseModel):
    viewer_stats: dict[str, Any]
