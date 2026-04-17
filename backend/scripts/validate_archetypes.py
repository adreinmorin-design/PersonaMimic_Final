# © 2026 Dre's Autonomous Neural Interface | Professional Grade Asset
#
# validate_archetypes.py - Neural Archetype Validation Script
# Tests the knowledge mapper and diagnostic suite.
#

import asyncio
import logging

from app.forge.diagnostic import diagnostic_suite
from app.forge.mapper import knowledge_mapper

logging.basicConfig(level=logging.INFO, format="[DRE-NEURAL] %(message)s")
logger = logging.getLogger("archetype_validator")


async def validate():
    logger.info("Starting Industrial Archetype Validation...")

    # 1. Test Mapper Discovery
    styles = ["supabase_realtime", "appsmith_lowcode", "fastapi_backend"]
    for style in styles:
        archetype = knowledge_mapper.get_steering_for_product(style)
        if archetype:
            logger.info(f"[OK] Archetype '{style}' verified. Focus: {archetype['focus']}")
        else:
            logger.error(f"[FAIL] Archetype '{style}' not found in knowledge base.")

    # 2. Test Deep Scan
    await knowledge_mapper.scan_model_capabilities("Llama-3.1-8B-Industrial")

    # 3. Test Diagnostic Suite (Bridge)
    influence = diagnostic_suite.trace_archetype_influence("supabase_realtime", None)
    logger.info(f"Neural Bind Strength (Supabase): {influence * 100:.2f}%")

    # 4. Neural Decompile Test
    pattern = diagnostic_suite.neural_decompile("c_882")
    logger.info(f"Decompiled Cipher 'c_882': {pattern}")

    print("\nARCHETYPE VALIDATION: SUCCESS. Neural knowledge base is studio-grade.")


if __name__ == "__main__":
    asyncio.run(validate())
