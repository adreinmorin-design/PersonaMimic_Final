# © 2026 Dre's Autonomous Neural Interface | Professional Grade Asset
#
# whop_api.py - Industrial Whop API Integration
# Handles product publishing and community engagement.

import logging
from typing import Any, Dict

import aiohttp

logger = logging.getLogger("swarm.tools.whop_api")

WHOP_BASE_URL = "https://api.whop.com/v1"


async def whop_request(
    method: str, endpoint: str, api_key: str, data: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """Unified Whop API request handler."""
    url = f"{WHOP_BASE_URL}/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(
                method, url, headers=headers, json=data, timeout=15
            ) as response:
                res_data = await response.json() if response.status != 204 else {}
                if response.status >= 400:
                    logger.error(f"Whop API Error ({response.status}): {res_data}")
                    return {"error": res_data, "status": response.status}
                return res_data
        except Exception as e:
            logger.error(f"Whop Request Fault: {e}")
            return {"error": str(e), "status": 500}


async def create_whop_product(
    api_key: str, title: str, description: str, price: float
) -> Dict[str, Any]:
    """Create a new digital product on Whop."""
    payload = {"name": title, "description": description, "visibility": "visible"}
    # Note: Creating plans usually requires a separate call or nested payload depending on API version
    return await whop_request("POST", "products", api_key, payload)


async def create_whop_post(api_key: str, experience_id: str, content: str) -> Dict[str, Any]:
    """Publish a community post/announcement."""
    payload = {"content": content}
    return await whop_request("POST", f"experiences/{experience_id}/posts", api_key, payload)


async def list_whop_experiences(api_key: str) -> Dict[str, Any]:
    """List all experiences to find the community/forum ID."""
    return await whop_request("GET", "experiences", api_key)
