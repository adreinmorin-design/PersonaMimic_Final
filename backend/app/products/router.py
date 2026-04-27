from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.paths import WORKSPACE_DIR
from app.database.database import get_db
from app.products.schemas import ProductsListResponse, RevenueResponse, WhopWebhook
from app.products.service import products_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductsListResponse)
async def get_products(db: Session = Depends(get_db)):
    return {"products": products_service.get_product_summaries(db)}


@router.get("/revenue", response_model=RevenueResponse)
async def get_revenue(db: Session = Depends(get_db)):
    return products_service.get_revenue_metrics(db)


@router.post("/webhook/whop")
async def whop_webhook(webhook: WhopWebhook, db: Session = Depends(get_db)):
    return products_service.handle_whop_webhook(db, webhook.type, webhook.data)


@router.get("/download/{filename}")
async def download_product(filename: str):
    """Serve packaged zips from the workspace."""
    fpath = WORKSPACE_DIR / filename
    if not fpath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(fpath, media_type="application/zip", filename=filename)
