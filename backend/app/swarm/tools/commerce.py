import os
import json
import logging
import zipfile
import requests
from pydantic import BaseModel
from typing import Any

from app.database.database import SessionLocal
from app.products.repository import product_repo
from .base import (
    FACTORY_MIN_SCORE, _infer_product_files, _resolve_workspace_path, 
    _iter_workspace_files, _normalize_product_name, _assess_publish_readiness,
    _build_snapshot_for_files, _is_failure_result, _persist_product_state, 
    _dedupe_preserve
)

logger = logging.getLogger("swarm.tools.commerce")

class EcommerceArgs(BaseModel):
    platform: str
    api_key: str | None = None
    title: str
    description: str
    price: float
    currency: str = "USD"
    company_id: str | None = None

def package_product(product_name: str, files: list = None):
    """Zip workspace files into a product archive."""
    try:
        from .quality import _verify_quality_gate
        selected = _infer_product_files(product_name, files)
        verdict = _verify_quality_gate(product_name, selected)
        if not verdict["passed"]:
            return f"Packaging blocked: Score {verdict['score']}/{FACTORY_MIN_SCORE}"
        
        zip_name = f"{_normalize_product_name(product_name)}.zip"
        zip_path = _resolve_workspace_path(zip_name)
        count = 0
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for abs_p, rel_p in _iter_workspace_files(selected):
                if rel_p != zip_name:
                    zf.write(abs_p, arcname=rel_p); count += 1
        
        _persist_product_state(product_name, status="packaged", path=zip_path, score=verdict["score"])
        return f"SUCCESS: Packaged {zip_path} ({count} files)."
    except Exception as e: return f"Packaging error: {str(e)}"

def list_products():
    """List all digital products in the database."""
    db = SessionLocal()
    try:
        products = product_repo.list_all(db)
        if not products: return "No products found."
        return "\n".join([f"* {p.name} | Status: {p.status} | URL: {p.url or 'N/A'}" for p in products])
    finally: db.close()

def ecommerce_publisher(platform: str, api_key: str = None, title: str = "product", description: str = "", price: float = 0, currency: str = "USD", company_id: str = None):
    """Publish product to Gumroad, Whop, or Stripe."""
    try:
        from .base import _assess_publish_readiness, _build_snapshot_for_files
        ready = _ensure_publish_ready_product(title)
        # Simplified publishing logic
        match platform.lower():
            case "gumroad": return f"[OK] Gumroad product live! (Simulated)"
            case "whop": return f"[OK] Whop product live! (Simulated)"
            case "stripe": return f"[OK] Stripe product created. (Simulated)"
            case _: return "Unsupported platform."
    except Exception as e: return f"Publisher error: {str(e)}"

def revenue_auditor(days: int = 7):
    """Sync real sales data."""
    return json.dumps({"total_revenue": "$0.00 (Simulated)"})

# --- Internal Helpers ---

def _find_product_record(db, name: str, allow_publish_ready_fallback: bool = False):
    product = product_repo.find_by_name(db, name)
    if product: return product
    norm = _normalize_product_name(name)
    fuzzy = product_repo.find_fuzzy(db, norm)
    if fuzzy: return fuzzy
    if allow_publish_ready_fallback:
        ready = [c for c in product_repo.list_all(db) if c.path and os.path.exists(c.path) and (c.adversary_score or 0) >= FACTORY_MIN_SCORE]
        if len(ready) == 1: return ready[0]
    return None

def _ensure_publish_ready_product(product_name: str):
    db = SessionLocal()
    try:
        p = _find_product_record(db, product_name, allow_publish_ready_fallback=True)
        if p and p.path and os.path.exists(p.path) and (p.adversary_score or 0) >= FACTORY_MIN_SCORE and p.status in {"packaged", "published"}:
            return {"name": p.name, "path": p.path, "score": p.adversary_score or 0, "status": p.status}
    finally: db.close()

    p_target = p.name if p else product_name
    res = package_product(p_target, _infer_product_files(p_target))
    if _is_failure_result(res): raise RuntimeError(res)

    db = SessionLocal()
    try:
        p = _find_product_record(db, product_name, allow_publish_ready_fallback=True)
        if not p or not p.path or not os.path.exists(p.path):
            raise RuntimeError("Packaging failed to produce artifact.")
        return {"name": p.name, "path": p.path, "score": p.adversary_score or 0, "status": p.status}
    finally: db.close()
