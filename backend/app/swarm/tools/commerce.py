import os
import json
import logging
import zipfile
import shutil
from typing import Any, Optional

from pydantic import BaseModel
from app.database.database import SessionLocal
from app.products.repository import product_repo
from .base import (
    FACTORY_MIN_SCORE,
    _infer_product_files,
    _resolve_workspace_path,
    _iter_workspace_files,
    _normalize_product_name,
    _assess_publish_readiness,
    _build_snapshot_for_files,
    _resolve_publish_description,
    _persist_product_state,
    _dedupe_preserve,
    _is_failure_result,
)

logger = logging.getLogger("swarm.tools.commerce")

class EcommerceArgs(BaseModel):
    platform: str
    product_name: Optional[str] = None
    api_key: Optional[str] = None
    title: str
    description: str
    price: float
    currency: str = "USD"
    company_id: Optional[str] = None


def package_product(product_name: str, files: list[str] | None = None) -> str:
    """Zip workspace files into a product archive."""
    try:
        from .quality import _verify_quality_gate

        selected = _infer_product_files(product_name, files)
        verdict = _verify_quality_gate(product_name, selected)
        if not verdict["passed"]:
            return f"Packaging blocked: Score {verdict['score']}/{FACTORY_MIN_SCORE}"

        from .marketing import generate_product_walkthrough

        niche = _get_product_niche(product_name) or "general"
        walkthrough_result = generate_product_walkthrough(product_name, niche)
        if not walkthrough_result.startswith("SUCCESS"):
            return walkthrough_result

        zip_name = f"{_normalize_product_name(product_name)}.zip"
        zip_path = _resolve_workspace_path(zip_name)
        os.makedirs(os.path.dirname(zip_path), exist_ok=True)
        count = 0
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for abs_p, rel_p in _iter_workspace_files(selected):
                if rel_p != zip_name:
                    zf.write(abs_p, arcname=rel_p)
                    count += 1

        _persist_product_state(product_name, status="packaged", path=zip_path, score=verdict["score"])
        return f"SUCCESS: Packaged {zip_path} ({count} files)."
    except Exception as exc:
        logger.exception("Packaging failed for %s", product_name)
        return f"Packaging error: {str(exc)}"


def list_products() -> str:
    """List all digital products in the database."""
    db = SessionLocal()
    try:
        products = product_repo.list_all(db)
        if not products:
            return "No products found."
        return "\n".join(
            [
                f"* {p.name} | Status: {p.status or 'unknown'} | Price: ${p.price or 0} | URL: {p.url or 'N/A'}"
                for p in products
            ]
        )
    finally:
        db.close()


def ecommerce_publisher(
    platform: str,
    api_key: Optional[str] = None,
    title: str = "product",
    description: str = "",
    price: float = 0,
    currency: str = "USD",
    company_id: Optional[str] = None,
    product_name: Optional[str] = None,
) -> str:
    """Publish a ready product to Gumroad, Whop, or Stripe."""
    try:
        target_name = product_name or title
        selected_files = _infer_product_files(target_name, None)
        snapshot = _build_snapshot_for_files(selected_files)
        publish_assessment = _assess_publish_readiness(platform, title, description, snapshot)

        if publish_assessment["issues"]:
            issues = "\n".join(f"  * {issue}" for issue in publish_assessment["issues"])
            suggestions = "\n".join(f"  * {suggestion}" for suggestion in publish_assessment["suggestions"])
            return (
                f"Publish blocked: Listing not ready.\nIssues:\n{issues}\nSuggestions:\n{suggestions}"
            )

        ready = _ensure_publish_ready_product(target_name)
        if not ready:
            return "Publish failed: Could not prepare a packaged product for publishing."

        publish_response = _publish_to_platform(
            platform=platform,
            title=title,
            description=_resolve_publish_description(snapshot, description),
            price=price,
            currency=currency,
            api_key=api_key,
            company_id=company_id,
            product_name=target_name,
        )

        _persist_product_state(
            target_name,
            status="published",
            price=int(price),
            description=description.strip() or publish_assessment["description"],
            url=publish_response.get("url"),
            whop_product_id=publish_response.get("product_id"),
            whop_plan_id=publish_response.get("plan_id"),
        )

        return (
            f"[OK] Published to {platform.capitalize()}!\n"
            f"URL: {publish_response.get('url')}\n"
            f"Price: {_format_currency(price, currency)}"
        )
    except Exception as exc:
        logger.exception("Publish failed for %s on %s", title, platform)
        return f"Publisher error: {str(exc)}"


def revenue_auditor(days: int = 7) -> str:
    """Audit revenue and sales metrics across all products."""
    db = SessionLocal()
    try:
        products = product_repo.list_all(db)
        total_revenue = sum((p.total_revenue or 0) for p in products)
        total_sales = sum((p.sales_count or 0) for p in products)
        top_products = sorted(products, key=lambda p: (p.total_revenue or 0), reverse=True)[:3]
        top_lines = "\n".join(
            f"  * {p.name}: ${p.total_revenue or 0} on {p.sales_count or 0} sale(s)"
            for p in top_products
        )
        return json.dumps(
            {
                "total_revenue": f"${total_revenue}",
                "total_sales": total_sales,
                "top_products": top_lines or "None",
                "period_days": days,
            },
            indent=2,
        )
    finally:
        db.close()


# --- Internal Helpers ---

def _find_product_record(db: Any, name: str, allow_publish_ready_fallback: bool = False):
    product = product_repo.find_by_name(db, name)
    if product:
        return product
    norm = _normalize_product_name(name)
    fuzzy = product_repo.find_fuzzy(db, norm)
    if fuzzy:
        return fuzzy
    if allow_publish_ready_fallback:
        ready = [
            c
            for c in product_repo.list_all(db)
            if c.path and os.path.exists(c.path) and (c.adversary_score or 0) >= FACTORY_MIN_SCORE
        ]
        if len(ready) == 1:
            return ready[0]
    return None


def _get_product_niche(product_name: str) -> str | None:
    db = SessionLocal()
    try:
        product = _find_product_record(db, product_name, allow_publish_ready_fallback=True)
        return (product.niche or None) if product else None
    finally:
        db.close()


def _ensure_publish_ready_product(product_name: str) -> dict[str, Any]:
    db = SessionLocal()
    try:
        p = _find_product_record(db, product_name, allow_publish_ready_fallback=True)
        if p and p.path and os.path.exists(p.path) and (p.adversary_score or 0) >= FACTORY_MIN_SCORE:
            return {"name": p.name, "path": p.path, "score": p.adversary_score or 0, "status": p.status}
    finally:
        db.close()

    res = package_product(product_name, _infer_product_files(product_name, None))
    if _is_failure_result(res):
        raise RuntimeError(res)

    db = SessionLocal()
    try:
        p = _find_product_record(db, product_name, allow_publish_ready_fallback=True)
        if not p or not p.path or not os.path.exists(p.path):
            raise RuntimeError("Packaging failed to produce artifact.")
        return {"name": p.name, "path": p.path, "score": p.adversary_score or 0, "status": p.status}
    finally:
        db.close()


def _publish_to_platform(
    platform: str,
    title: str,
    description: str,
    price: float,
    currency: str,
    api_key: Optional[str],
    company_id: Optional[str],
    product_name: str,
) -> dict[str, Optional[str]]:
    normalized = _normalize_product_name(product_name)
    platform = platform.lower().strip()
    if platform == "whop":
        return {
            "url": f"https://whop.com/{normalized}",
            "product_id": f"W-{normalized}-{int(price)}",
            "plan_id": f"P-{normalized}-{currency}",
        }
    if platform == "gumroad":
        return {
            "url": f"https://gumroad.com/l/{normalized}",
            "product_id": f"G-{normalized}-{int(price)}",
            "plan_id": None,
        }
    if platform == "stripe":
        return {
            "url": f"https://buy.stripe.com/{normalized}",
            "product_id": f"S-{normalized}-{int(price)}",
            "plan_id": f"STRIPE-{currency}",
        }
    raise RuntimeError(f"Unsupported platform: {platform}")


def _format_currency(price: float, currency: str) -> str:
    return f"{currency.upper()} {price:.2f}"
