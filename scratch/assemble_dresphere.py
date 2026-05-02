# © 2026 Dre's Autonomous Neural Interface | Professional Grade Asset
#
# assemble_dresphere.py - Industrial Assembly Bootstrap
# Orchestrates the full synthesis and assembly of the DreSphere platform.

import asyncio
import json
import logging
import sys
import os
import re

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.swarm.tools.engineering import assemble_full_product

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("assembly_mission")


def clean_json_markdown(text):
    """Strips markdown code blocks from the directive string."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```json\n?", "", text)
        text = re.sub(r"```$", "", text)
    return text.strip()


async def run_assembly():
    logger.info("[*] Phase 1: Loading Industrial Build Directive...")

    results_path = "scratch/discovery_results.json"
    if not os.path.exists(results_path):
        logger.error("[X] Discovery results not found. Run discovery_mission_01.py first.")
        return

    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    niche = data["niche"]
    raw_directive = data["directive"]

    try:
        directive_json = clean_json_markdown(raw_directive)
        directive = json.loads(directive_json)

        product_name = directive["product_name"]
        product_type = directive["product_type"]
        specs = json.dumps(directive["specs"])  # Passing full spec object as string

        logger.info(f"[*] Launching Studio-Grade Assembly for '{product_name}'...")
        logger.info(f"[*] Product Type: {product_type}")
        logger.info("[*] This process involves multi-brain coordination. Please wait...")

        assembly_log = await assemble_full_product(
            product_name=product_name, niche=niche, product_type=product_type, specs=specs
        )

        print("\n=== ASSEMBLY LOG ===")
        print(assembly_log)
        print("====================\n")

        logger.info(f"[+] Assembly Complete. Artifacts stored in workspace/{product_name}/")

    except Exception as e:
        logger.error(f"[X] Assembly Fault: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_assembly())
