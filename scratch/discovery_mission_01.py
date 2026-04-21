# © 2026 Dre's Autonomous Neural Interface | Professional Grade Asset
#
# discovery_mission_01.py - Industrial Discovery Bootstrap
# Executes the new high-complexity discovery loop.

import asyncio
import json
import logging
import sys
import os

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.swarm.tools.discovery import discover_new_niche, market_research, market_analyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discovery_mission")


async def run_mission():
    logger.info("[*] Phase 1: Scanning for Hyper-Trending Niche...")
    niche = await discover_new_niche()
    logger.info(f"[+] Identified Niche: {niche}")

    logger.info(f"[*] Phase 2: Conducting Deep Market Research on '{niche}'...")
    research_data = await market_research(niche)
    logger.info("[+] Research Complete. (Data density: High)")

    logger.info("[*] Phase 3: Synthesizing Industrial Build Directive...")
    directive_json = await market_analyzer(research_data, niche)

    try:
        directive = json.loads(directive_json)
        print("\n=== INDUSTRIAL BUILD DIRECTIVE ===")
        print(json.dumps(directive, indent=2))
        print("==================================\n")

        # Save results for swarm consumption
        with open("scratch/discovery_results.json", "w", encoding="utf-8") as f:
            json.dump({"niche": niche, "directive": directive}, f, indent=2)

    except Exception as e:
        logger.error(f"[X] Analysis Parse Fault: {e}")
        print(f"Raw Directive: {directive_json}")


if __name__ == "__main__":
    asyncio.run(run_mission())
