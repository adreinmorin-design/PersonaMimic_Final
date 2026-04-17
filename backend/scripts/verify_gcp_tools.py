import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from app.swarm.tools import maps_search, web_search


def test_google_tools():
    key = os.getenv("GOOGLE_API_KEY")
    print(f"[*] Debug: GOOGLE_API_KEY starts with: {key[:4] if key else 'None'}")
    print("[*] Testing Industrial Search (GCP Custom Search API)...")
    search_res = web_search("industrial digital factory trends 2025")
    print(f"[RESULT] Search:\n{search_res[:500]}...")

    print("\n[*] Testing Geospatial Intelligence (Google Maps API)...")
    maps_res = maps_search("high growth Coworking Spaces in Austin TX")
    print(f"[RESULT] Maps:\n{maps_res}")


if __name__ == "__main__":
    test_google_tools()
