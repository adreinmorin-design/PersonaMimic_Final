from typing import Any

from pydantic import BaseModel


class WhopWebhook(BaseModel):
    type: str
    data: dict[str, Any]


class ProductResponse(BaseModel):
    id: int
    name: str
    status: str
    url: str | None
    path: str | None
    description: str | None
    price: int | None
    category: str | None
    created_at: str


class ProductsListResponse(BaseModel):
    products: list[ProductResponse]


class RevenueResponse(BaseModel):
    revenue: float
    daily_growth: str
    active_customers: int
    sales_count: int
