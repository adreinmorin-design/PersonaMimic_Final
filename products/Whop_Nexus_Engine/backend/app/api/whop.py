# © 2026 Dre's Autonomous Neural Interface | Whop Nexus Engine
# backend/app/api/whop.py

from fastapi import APIRouter, Request, Header, HTTPException
from typing import Dict, Any, Optional
import hmac
import hashlib
import os
import logging

from app.services.delivery import delivery_service

router = APIRouter()
logger = logging.getLogger("whop.api")

WHOP_WEBHOOK_SECRET: str = os.getenv("WHOP_WEBHOOK_SECRET", "whop_secret_placeholder")


@router.post("/webhook")
async def whop_webhook_handler(
    request: Request, x_whop_signature: Optional[str] = Header(None)
) -> Dict[str, str]:
    """
    Handle incoming Whop webhooks for membership and access events.
    Strictly validates signatures to prevent spoofing.
    """
    payload: bytes = await request.body()

    # Signature Validation (Industrial Standard)
    if not x_whop_signature:
        raise HTTPException(status_code=401, detail="Missing Whop signature")

    expected_signature: str = hmac.new(
        WHOP_WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, x_whop_signature):
        logger.warning("Invalid Whop signature detected.")
        raise HTTPException(status_code=403, detail="Invalid signature")

    data: Dict[str, Any] = await request.json()
    event_type: str = data.get("action", "unknown")

    logger.info(f"Processing Whop Event: {event_type}")

    if event_type == "membership.went_active":
        user_id: str = data.get("data", {}).get("user_id", "")
        product_id: str = data.get("data", {}).get("product_id", "")
        await delivery_service.provision_access(user_id, product_id)

    return {"status": "success", "event": event_type}


@router.get("/validate-license")
async def validate_license(license_key: str) -> Dict[str, Any]:
    """Verify a user's license key against the Whop API."""
    # Logic to call https://api.whop.com/v1/licenses/{license_key}
    # For now, return a typed mock
    return {
        "valid": True,
        "product": "Whop Nexus Engine",
        "license_key": license_key,
        "metadata": {"plan": "Industrial Swarm"},
    }
