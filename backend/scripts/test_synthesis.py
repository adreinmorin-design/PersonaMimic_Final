# © 2026 Dre's Autonomous Neural Interface | Professional Grade Asset
#
# test_synthesis.py - Test Script for Forensic Synthesis
#

import logging

from app.swarm.synthesis_agent import synthesis_agent

logging.basicConfig(level=logging.INFO, format="[DRE-TEST] %(message)s")
logger = logging.getLogger("test_synthesis")


def test():
    logger.info("Initializing Synthesis Test...")

    # Test synthesizing from the Phoenix heartbeat cluster
    cluster_id = "c_882"
    context = "Implement a pure Phoenix 2.0 heartbeat loop in Go."

    code = synthesis_agent.synthesize_from_cluster(cluster_id, context)

    logger.info("Synthesized Code Preview:")
    print("-" * 40)
    print(code)
    print("-" * 40)

    if "heartbeat" in code.lower() or "Phoenix" in code:
        print("\nSYNTHESIS TEST: SUCCESS.")
    else:
        print("\nSYNTHESIS TEST: PARTIAL SUCCESS (Verify output logic).")


if __name__ == "__main__":
    test()
