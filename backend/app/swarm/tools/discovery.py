import json
import logging

from app.swarm.persona_engine import PersonaEngine

from .search import web_search

logger = logging.getLogger("swarm.tools.discovery")


async def market_research(niche: str) -> str:
    """Research a niche for high-value underserved needs and complex technical pain points."""
    # Focused on high-value industrial needs and complex pain points
    search_query: str = (
        f"high-value industrial needs {niche} 2026 complex pain points underserved latent demand"
    )
    search_res: str = await web_search(search_query)
    results: list[str] = [f"Advanced Consumer Demand Research for '{niche}':\n" + search_res]
    return "\n\n".join(results)[:4000]


async def market_analyzer(raw_data: str, niche: str = "") -> str:
    """Convert research into a high-complexity industrial build directive."""
    try:
        engine: PersonaEngine = PersonaEngine()
        prompt: str = (
            f"Perform a deep forensic analysis of this research for '{niche}':\n\n{raw_data}\n\n"
            "TASK: Design an Industrial-Scale Digital Product that solves the identified high-value pain points.\n"
            "REQUIREMENTS:\n"
            "1. Complexity: The product must be a multi-module system (e.g. Ingestion + AI + UI).\n"
            "2. Scalability: Design for high throughput and industrial-grade reliability.\n"
            "3. Specs: Include detailed features, suggested tech stack (Go/Rust/Python), and 8-10 essential files.\n"
            'Output ONLY a JSON build directive: {"product_name": "...", "product_type": "...", "specs": "...", "complexity": "INDUSTRIAL"}.'
        )
        res: dict = await engine.generate_response(prompt, persona_type="reasoning")
        return json.dumps(res.get("content", {}))
    except Exception as e:
        return f"Market analysis fault: {str(e)}"


async def discover_new_niche(depth: int = 5) -> str:
    """Scan for hyper-trending, high-demand digital product niches."""
    try:
        engine: PersonaEngine = PersonaEngine()
        # Focused on viral trends and underserved needs
        trends: str = await web_search(
            "hyper-viral digital product trends 2026 underserved needs pain points"
        )
        prompt: str = f"Analyze these trending needs and pain points:\n{trends}\nIdentify ONE specific high-demand niche. Output ONLY the name."
        res: dict = await engine.generate_response(prompt, persona_type="mimic")
        return res.get("content", "").strip().strip("'").strip('"') or "High-Demand Digital Assets"
    except Exception:
        return "Consumer-Driven Productivity Tools"


async def predictive_market_scout(current_niche: str) -> str:
    """Extrapolate future needs and latent demand for a niche."""
    try:
        engine: PersonaEngine = PersonaEngine()
        research: str = await market_research(current_niche)
        prompt: str = (
            f"Based on current research for '{current_niche}':\n{research}\n\n"
            "TASK: Perform 'Predictive Synthesis'.\n"
            "1. Identify 3 latent (hidden) needs that people don't know they have yet.\n"
            "2. Predict a non-obvious digital product that will be trending in 6-12 months.\n"
            "3. Explore a 'wildcard' idea that combines this niche with a different viral trend.\n"
            "Output ONLY a clean MARKDOWN report."
        )
        res: dict = await engine.generate_response(prompt, persona_type="reasoning")
        return res.get("content", "No predictive data available.")
    except Exception as e:
        return f"Scout error: {str(e)}"


async def add_to_global_niches(niche: str) -> str:
    """Persistently record a discovered niche."""
    try:
        from app.config.service import NICHES

        if niche not in NICHES:
            NICHES.append(niche)
            return f"SUCCESS: '{niche}' added."
        return f"INFO: '{niche}' already known."
    except Exception as e:
        return f"Memory fault: {str(e)}"


async def affiliate_researcher(niche: str, min_commission: float = 20.0) -> str:
    """Find affiliate opportunities."""
    try:
        engine: PersonaEngine = PersonaEngine()
        raw: str = await web_search(f"best high ticket affiliate programs for {niche}")
        res: dict = await engine.generate_response(
            f"List top 3 programs from:\n{raw}\nONLY Markdown table.", persona_type="mimic"
        )
        return res.get("content", "No programs found.")
    except Exception as e:
        return f"Researcher error: {str(e)}"
