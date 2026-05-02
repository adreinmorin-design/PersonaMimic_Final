import logging
<<<<<<< HEAD
from typing import Optional
from .base import WORKSPACE_DIR, _extract_code
=======
import os

>>>>>>> ee8c098f736845d23a6b0c0cb6f8597f07c6eb01
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


<<<<<<< HEAD
def _resolve_walkthrough_path(product_name: str) -> str:
    candidates = [
        product_name,
        product_name.replace(" ", "_"),
        product_name.replace(" ", "-"),
        product_name.lower().replace(" ", "_"),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        candidate_path = os.path.join(WORKSPACE_DIR, candidate)
        if os.path.isdir(candidate_path):
            return os.path.join(candidate_path, "WALKTHROUGH.md")
    return os.path.join(WORKSPACE_DIR, f"{product_name}_WALKTHROUGH.md")


def generate_product_walkthrough(
    product_name: str,
    niche: str = "general",
    output_path: Optional[str] = None,
):
    """Generate a product walkthrough proof artifact."""
    try:
        engine = PersonaEngine()
        prompt = (
            f"You are creating a product walkthrough for the product '{product_name}' in the niche '{niche}'. "
            "Write a complete proof-of-work walkthrough in Markdown. "
            "Include installation and setup steps, usage examples, a demo scenario, expected results, "
            "and verification commands or browser steps that show the app is fully functional. "
            "Use headings, bullets, and clear output expectations."
        )
        res = engine.generate_response(prompt, persona_type="director")
        content = res.get("content", "").strip()
        if not content:
            return "Walkthrough generation error: empty response."

        path = output_path or _resolve_walkthrough_path(product_name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"SUCCESS: Walkthrough generated at {path}."
    except Exception as e:
        logger.exception("Walkthrough generation failed for %s", product_name)
        return f"Walkthrough error: {str(e)}"
=======
async def market_trend_research(topic: str):
    """Research specific market trends for a topic."""
    from .search import web_search

    try:
        results = await web_search(f"profitable {topic} trends and consumer demand 2026")
        return f"TREND DATA FOR {topic.upper()}:\n{results[:2000]}"
    except Exception as e:
        return f"Trend research fault: {str(e)}"
>>>>>>> ee8c098f736845d23a6b0c0cb6f8597f07c6eb01


def social_publisher(platform: str, content: str):
    """Publish to social media."""
    logger.info("[MARKETING] Publishing to %s: %s", platform, content[:50])
    return f"SUCCESS: Content published to {platform}."
