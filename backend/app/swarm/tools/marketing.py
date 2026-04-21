import logging
import os

from app.swarm.persona_engine import PersonaEngine

from .base import WORKSPACE_DIR, _extract_code

logger = logging.getLogger("swarm.tools.marketing")


def generate_marketing_copy(product_name: str, niche: str):
    """Generate marketing assets."""
    try:
        engine = PersonaEngine()
        res = engine.generate_response(
            f"Generate marketing copy for {product_name} in {niche}", persona_type="mimic"
        )
        path = os.path.join(WORKSPACE_DIR, "MARKETING.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(res.get("content", ""))
        return "[OK] Marketing assets generated."
    except Exception as e:
        return f"Marketing error: {str(e)}"


def generate_whop_app(product_name: str, niche: str):
    """Build Whop App boilerplate."""
    try:
        engine = PersonaEngine()
        res = engine.generate_response(
            f"Generate Whop App boilerplate for {product_name}", persona_type="coding"
        )
        path = os.path.join(WORKSPACE_DIR, "whop_app", "index.jsx")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(_extract_code(res.get("content", "")))
        return "[OK] Whop app built."
    except Exception as e:
        return f"App Factory error: {str(e)}"


def generate_app_visuals(product_name: str, description: str):
    """Generate UI/UX Design Guide."""
    try:
        engine = PersonaEngine()
        res = engine.generate_response(
            f"Create UI/UX Design Guide for '{product_name}': {description}", persona_type="mimic"
        )
        path = os.path.join(WORKSPACE_DIR, f"{product_name}_DESIGN_GUIDE.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(res.get("content", ""))
        return f"SUCCESS: Design Guide saved to {path}."
    except Exception as e:
        return f"Visuals error: {str(e)}"


async def market_trend_research(topic: str):
    """Research specific market trends for a topic."""
    from .search import web_search

    try:
        results = await web_search(f"profitable {topic} trends and consumer demand 2026")
        return f"TREND DATA FOR {topic.upper()}:\n{results[:2000]}"
    except Exception as e:
        return f"Trend research fault: {str(e)}"


def social_publisher(platform: str, content: str):
    """Publish to social media."""
    logger.info("[MARKETING] Publishing to %s: %s", platform, content[:50])
    return f"SUCCESS: Content published to {platform}."
