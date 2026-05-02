"""
app/swarm/flow_manager.py - Stateful LangGraph Orchestrator
Implements the 'Industrial Loop' (Generator -> Adversary -> Repair) using cyclic graphs.
"""

import logging
import time
import os
from typing import TypedDict, Optional

from langgraph.graph import END, StateGraph

from app.database.database import db_session as get_db
from app.products.repository import product_repo
from app.reverse_engineering.repository import reverse_engineering_repo
from app.reverse_engineering.schemas import SynthesisRequest
from app.swarm.synthesis_agent import synthesis_agent
from app.swarm.tools import execute_tool

logger = logging.getLogger("swarm.flow")

# Configuration for sequential step-by-step execution
STEP_BY_STEP_MODE = os.getenv("STEP_BY_STEP_MODE", "true").lower() == "true"
STEP_DELAY_SECONDS = float(os.getenv("STEP_DELAY_SECONDS", "2.0"))
CHECKPOINT_LOGGING = os.getenv("CHECKPOINT_LOGGING", "true").lower() == "true"


class StepExecutor:
    """Controller for sequential step-by-step execution with quality gates."""

    def __init__(self, enable_delays: bool = STEP_BY_STEP_MODE, delay_seconds: float = STEP_DELAY_SECONDS):
        self.enable_delays = enable_delays
        self.delay_seconds = delay_seconds
        self.step_count = 0
        self.completed_steps = []

    def execute_step(self, step_name: str, step_func, state: dict) -> dict:
        """Execute a single step with logging, delays, and checkpoints."""
        self.step_count += 1
        step_id = f"STEP-{self.step_count}"

        logger.info(f"[CHECKPOINT] {step_id}: Starting '{step_name}'")
        if CHECKPOINT_LOGGING:
            logger.debug(f"[CHECKPOINT] {step_id} Input State: product={state.get('product_name')}, niche={state.get('niche')}")

        start_time = time.time()

        try:
            result = step_func(state)
            elapsed = time.time() - start_time

            self.completed_steps.append({
                "step_id": step_id,
                "step_name": step_name,
                "status": "completed",
                "duration_seconds": round(elapsed, 2),
            })

            logger.info(
                f"[CHECKPOINT] {step_id}: Completed '{step_name}' in {elapsed:.2f}s | "
                f"Status: {result.get('status', 'unknown')}"
            )

            if self.enable_delays and self.delay_seconds > 0:
                logger.debug(f"[CHECKPOINT] {step_id}: Waiting {self.delay_seconds}s before next step...")
                time.sleep(self.delay_seconds)

            return result
        except Exception as e:
            elapsed = time.time() - start_time
            self.completed_steps.append({
                "step_id": step_id,
                "step_name": step_name,
                "status": "failed",
                "duration_seconds": round(elapsed, 2),
                "error": str(e),
            })
            logger.error(f"[CHECKPOINT] {step_id}: FAILED '{step_name}' after {elapsed:.2f}s: {str(e)}")
            raise

    def get_execution_summary(self) -> dict:
        """Return summary of all completed steps."""
        return {
            "total_steps": self.step_count,
            "completed_steps": len([s for s in self.completed_steps if s["status"] == "completed"]),
            "failed_steps": len([s for s in self.completed_steps if s["status"] == "failed"]),
            "total_duration": sum(s.get("duration_seconds", 0) for s in self.completed_steps),
            "steps": self.completed_steps,
        }


# Global executor instance
_step_executor = StepExecutor(enable_delays=STEP_BY_STEP_MODE, delay_seconds=STEP_DELAY_SECONDS)



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
        brain_name="Architect",
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
        brain_name="LegalMind",
    )
    
    # Register product in database so it appears in the dashboard
    with get_db() as db:
        await product_repo.update_state(
            db, 
            state["product_name"], 
            status="generated", 
            niche=state["niche"]
        )
        
    return {"status": "generated", "attempts": state["attempts"] + 1}


async def adversary_node(state: SwarmState):
    """Strict Quality Gate using Forensic/Static analysis (Step 2)."""
    def _validate():
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
        report_raw = execute_tool("objective_validator", {"product_name": state["product_name"]})
        passed = "PASSED" in report_raw or "Findings: 0" in report_raw
        score = 100.0 if passed else 0.0

        return {
            "adversary_report": {"raw": report_raw, "passed": passed},
            "forensic_score": score,
            "status": "validated" if passed else "correction_needed",
        }
    
    return _step_executor.execute_step("adversary", _validate, state)


async def healer_node(state: SwarmState):
    """Neural Self-Correction guided by Adversary metrics (Step 3)."""
    def _repair():
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
    
    return _step_executor.execute_step("healer", _repair, state)


async def synthesis_node(state: SwarmState):
    """Forensic synthesis: Forges code from neural clusters (Step 4)."""
    def _synthesize():
        logger.info(f"[FLOW] Executing Forensic Synthesis for {state['product_name']}...")

        cluster_id = "c_882" if "phoenix" in state.get("niche", "").lower() else "c_104"
        synthesis_result = await synthesis_agent.synthesize_from_cluster(cluster_id, state["specs"])
        generated_block = synthesis_result.get("code", "")
        purpose = synthesis_result.get("purpose", "Autonomous forensic integration.")

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
    
    return _step_executor.execute_step("synthesis", _synthesize, state)


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
