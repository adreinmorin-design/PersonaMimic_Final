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
    plan_details: dict


# --- Nodes ---
async def planner_node(state: SwarmState):
    """Refines the mission into detailed specs using the Top-Notch Orchestrator."""
    logger.info(f"[FLOW] Orchestrator planning mission for {state['niche']}...")

    res_json = await execute_tool(
        "strategic_planner",
        {"niche": state["niche"], "current_specs": state["specs"]},
        brain_name="MasterBrain",
    )

    import json

    try:
        data = json.loads(res_json)
        return {
            "product_name": data.get("product_name", state["product_name"]),
            "specs": data.get("refined_specs", state["specs"]),
            "plan_details": data,
            "status": "planned",
        }
    except Exception:
        return {"status": "planning_failed"}


async def generator_node(state: SwarmState):
    """Generates the initial product bundle."""
    logger.info(f"[FLOW] Generating {state['product_name']}...")
    # Leveraging the existing assemble_full_product tool
    await execute_tool(
        "assemble_full_product",
        {
            "product_name": state["product_name"],
            "niche": state["niche"],
            "product_type": "SaaS",
            "specs": state["specs"],
        },
        brain_name="Codesmith",
    )
    # Ensure legal/compliance docs are included to boost score
    await execute_tool(
        "generate_compliance_bundle",
        {
            "product_name": state["product_name"],
            "niche": state["niche"],
            "specs": state["specs"],
        },
        brain_name="MasterBrain",
    )
    return {"status": "generated", "attempts": state["attempts"] + 1}


async def adversary_node(state: SwarmState):
    """Strict Quality Gate using Forensic/Static analysis."""
    logger.info(
        f"[FLOW] Adversary auditing {state['product_name']} (Attempt {state['attempts']})..."
    )

    # 1. Real Quality Gate (Static Scan + LLM Review)
    report_raw = await execute_tool(
        "validate_product", {"product_name": state["product_name"]}, brain_name="Fenko"
    )

    # 2. Check verdict
    passed = "[OK] PASSED" in report_raw

    # Extract score if possible
    score = 0.0
    import re

    match = re.search(r"Score: (\d+)/100", report_raw)
    if match:
        score = float(match.group(1))

    return {
        "adversary_report": {"raw": report_raw, "passed": passed},
        "forensic_score": score,
        "status": "validated" if passed else "correction_needed",
    }


async def healer_node(state: SwarmState):
    """Neural Self-Correction guided by Adversary metrics."""
    logger.info(f"[FLOW] Healer repairing {state['product_name']}...")

    repair_directive = f"FIX THESE ERRORS: {state['adversary_report']['raw'][:1000]}"
    await execute_tool(
        "assemble_full_product",
        {
            "product_name": state["product_name"],
            "niche": state["niche"],
            "specs": state["specs"],
            "feedback": state["adversary_report"].get("raw", "General repair needed."),
        },
        brain_name="Dre",
    )
    return {"status": "repaired"}


async def synthesis_node(state: SwarmState):
    """Forensic synthesis: Forges code directly from neural clusters if required."""
    logger.info(f"[FLOW] Executing Forensic Synthesis for {state['product_name']}...")

    # We use a default 'cluster_id' if specified in the specs, or fall back to General Logic
    cluster_id = "c_882" if "phoenix" in state.get("niche", "").lower() else "c_104"

    synthesis_result = await synthesis_agent.synthesize_from_cluster(cluster_id, state["specs"])
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
            job = await reverse_engineering_repo.create_job(db, req)
            await reverse_engineering_repo.update_job_status(
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
    workflow.add_node("planner", planner_node)
    workflow.add_node("generator", generator_node)
    workflow.add_node("adversary", adversary_node)
    workflow.add_node("healer", healer_node)
    workflow.add_node("synthesizer", synthesis_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "generator")
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
