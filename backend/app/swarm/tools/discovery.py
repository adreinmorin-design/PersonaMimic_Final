import json
import logging
from .base import _extract_code
from .search import web_search
from app.swarm.persona_engine import PersonaEngine

logger = logging.getLogger("swarm.tools.discovery")

def market_research(niche: str):
    """Research a niche for profitable products."""
    results = [f"Top search results for '{niche}':\n" + web_search(f"best selling products {niche} 2025")]
    return "\n\n".join(results)[:3000]

def market_analyzer(raw_data: str, niche: str = ""):
    """Convert research into a precise build directive."""
    try:
        engine = PersonaEngine()
        prompt = f"Analyze research for '{niche}':\n\n{raw_data}\n\nOutput JSON build directive (product_name, product_type, specs)."
        res = engine.generate_response(prompt, persona_type="mimic")
        return json.dumps(res.get("content", {}))
    except Exception as e: return f"Market analysis fault: {str(e)}"

def discover_new_niche(depth: int = 5):
    """Scan for trending, untapped niches."""
    try:
        engine = PersonaEngine()
        trends = web_search("hyper-viral digital product trends 2026")
        prompt = f"Analyze trends:\n{trends}\nIdentify ONE specific niche. Output ONLY the name."
        res = engine.generate_response(prompt, persona_type="mimic")
        return res.get("content", "").strip().strip("'").strip('"') or "Emerging Digital Assets"
    except Exception as e: return "Micro-SaaS Productivity Utilities"

def add_to_global_niches(niche: str):
    """Persistently record a discovered niche."""
    try:
        from app.config.service import NICHES
        if niche not in NICHES:
            NICHES.append(niche); return f"SUCCESS: '{niche}' added."
        return f"INFO: '{niche}' already known."
    except Exception as e: return f"Memory fault: {str(e)}"

def affiliate_researcher(niche: str, min_commission: float = 20.0):
    """Find affiliate opportunities."""
    try:
        engine = PersonaEngine()
        raw = web_search(f"best high ticket affiliate programs for {niche}")
        res = engine.generate_response(f"List top 3 programs from:\n{raw}\nONLY Markdown table.", persona_type="mimic")
        return res.get("content", "No programs found.")
    except Exception as e: return f"Researcher error: {str(e)}"
