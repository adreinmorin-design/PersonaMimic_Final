import os
import requests
import logging
from .base import tool_cache, SearchArgs

logger = logging.getLogger("swarm.tools.search")

try:
    from googlesearch import search as gsearch
except ImportError:
    gsearch = None

def _run_search_query(query: str, max_results: int = 5) -> list[str]:
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")

    if api_key and cse_id:
        try:
            url = f"https://customsearch.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={query}"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                items = res.json().get("items", [])
                return [item.get("link") for item in items[:max_results]]
        except Exception as exc:
            logger.warning("GCP Search failed: %s", exc)

    if not gsearch: return []
    try:
        return list(gsearch(query, num_results=max_results))
    except Exception as exc:
        logger.warning("Scraper search failed: %s", exc)
        return []

def web_search(query: str):
    """Search Google for market data, trends, and competitors."""
    results = _run_search_query(query, max_results=5)
    return "\n".join(results) if results else "Search returned no results."

def web_fetch(url: str):
    """Fetch the text content of any URL."""
    try:
        from bs4 import BeautifulSoup
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)[:3000]
    except Exception as e:
        return f"Fetch error: {str(e)}"

def maps_search(location_query: str):
    """Search for points of interest via Google Maps."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key: return "Error: GOOGLE_API_KEY missing."
    try:
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={location_query}&key={api_key}"
        res = requests.get(url, timeout=8)
        if res.status_code == 200:
            results = res.json().get("results", [])
            if not results: return "No locations found."
            output = [f"Geospatial results for '{location_query}':"]
            for r in results[:5]:
                output.append(f"* {r.get('name')} | Address: {r.get('formatted_address')} | Rating: {r.get('rating', 'N/A')}")
            return "\n".join(output)
        return f"Maps API Error: {res.text}"
    except Exception as e:
        return f"Maps Search Fault: {str(e)}"
