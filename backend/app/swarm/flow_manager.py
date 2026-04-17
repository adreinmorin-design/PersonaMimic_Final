"""
app/swarm/flow_manager.py - Stateful LangGraph Orchestrator
Implements the 'Industrial Loop' (Generator -> Adversary -> Repair) using cyclic graphs.
"""

import logging
from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.database.database import get_db
from app.reverse_engineering.repository import reverse_engineering_repo
from app.reverse_engineering.schemas import SynthesisRequest
from app.swarm.synthesis_agent import synthesis_agent
from app.swarm.tools import execute_tool

logger = logging.getLogger("swarm.flow")


class SwarmState(TypedDict):
    """The persistent state of an industrial task."""

    task_id: int
    product_name: str
    niche: str
    specs: str
    code_snapshot: dict[str, str]
    adversary_report: dict
    attempts: int
    max_attempts: int
    status: str
    forensic_score: float


# --- Nodes ---


def generator_node(state: SwarmState):
    """Generates the initial product bundle."""
    logger.info(f"[FLOW] Generating {state['product_name']}...")
    # Leveraging the existing assemble_full_product tool
    execute_tool(
        "assemble_full_product",
        {
            "product_name": state["product_name"],
            "niche": state["niche"],
            "product_type": "SaaS",
            "specs": state["specs"],
        },
    )
    return {"status": "generated", "attempts": state["attempts"] + 1}


def adversary_node(state: SwarmState):
    """Strict Quality Gate using Forensic/Static analysis."""
    logger.info(
        f"[FLOW] Adversary auditing {state['product_name']} (Attempt {state['attempts']})..."
    )

    # 1. Static Validation (Semgrep)
    report_raw = execute_tool("objective_validator", {"product_name": state["product_name"]})

    # 2. Forensic Analysis (if binary)
    # logic to call binary_analyzer if applicable...

    passed = "PASSED" in report_raw or "Findings: 0" in report_raw
    score = 100.0 if passed else 0.0  # Placeholder for actual heuristic scoring

    return {
        "adversary_report": {"raw": report_raw, "passed": passed},
        "forensic_score": score,
        "status": "validated" if passed else "correction_needed",
    }


def healer_node(state: SwarmState):
    """Neural Self-Correction guided by Adversary metrics."""
    logger.info(f"[FLOW] Healer repairing {state['product_name']}...")

    repair_directive = f"FIX THESE ERRORS: {state['adversary_report']['raw'][:1000]}"
    execute_tool(
        "assemble_full_product",
        {
            "product_name": state["product_name"],
            "niche": state["niche"],
            "specs": f"{state['specs']} | REPAIR_MODE: {repair_directive}",
        },
    )
    return {"status": "repaired"}


def synthesis_node(state: SwarmState):
    """Forensic synthesis: Forges code directly from neural clusters if required."""
    logger.info(f"[FLOW] Executing Forensic Synthesis for {state['product_name']}...")

    # We use a default 'cluster_id' if specified in the specs, or fall back to General Logic
    cluster_id = "c_882" if "phoenix" in state.get("niche", "").lower() else "c_104"

    synthesis_result = synthesis_agent.synthesize_from_cluster(cluster_id, state["specs"])
    generated_block = synthesis_result.get("code", "")
    purpose = synthesis_result.get("purpose", "Autonomous forensic integration.")

    # --- PERSIST ARTIFACT (#2 Visibility) ---
    with get_db() as db:
        try:
            req = SynthesisRequest(
                target=state.get("target_niche", state.get("niche", "Unknown")),
                cluster_id=cluster_id,
                context=state["specs"],
            )
            job = reverse_engineering_repo.create_job(db, req)
            reverse_engineering_repo.update_job_status(
                db, job.id, "completed", generated_block, purpose
            )
            logger.info(f"[FLOW] Persisted Synthesis Artifact to Vault: Job #{job.id}")
        except Exception as e:
            logger.error(f"[FLOW] Failed to persist synthesis artifact: {e}")

    return {"status": "synthesized"}


# --- Edges & Logic ---


def should_continue(state: SwarmState):
    if state["adversary_report"].get("passed"):
        return END
    if state["attempts"] >= state["max_attempts"]:
        logger.warning(f"[FLOW] Max attempts reached for {state['product_name']}. Haling cycle.")
        return END
    return "healer"


# --- Graph Construction ---


def create_swarm_graph():
    workflow = StateGraph(SwarmState)

    workflow.add_node("generator", generator_node)
    workflow.add_node("adversary", adversary_node)
    workflow.add_node("healer", healer_node)
    workflow.add_node("synthesizer", synthesis_node)

    workflow.set_entry_point("generator")
    workflow.add_edge("generator", "adversary")

    workflow.add_conditional_edges(
        "adversary",
        should_continue,
        {
            "healer": "healer",
            "synthesizer": "synthesizer",  # Optional branch
            END: END,
        },
    )

    workflow.add_edge("healer", "adversary")
    workflow.add_edge("synthesizer", "adversary")

    return workflow.compile()


# Singleton graph instance
swarm_workflow = create_swarm_graph()
