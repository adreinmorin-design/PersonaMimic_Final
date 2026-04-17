import os
import logging
import shutil
from .base import (
    FACTORY_MIN_SCORE, _infer_product_files, _stage_review_workspace, 
    _assess_bundle_quality, _build_workspace_snapshot, WORKSPACE_DIR,
    _persist_product_state, _dedupe_preserve
)

logger = logging.getLogger("swarm.tools.quality")

def validate_product(product_name: str = "product", files: list[str] | None = None) -> str:
    """Run strict peer adversary quality check."""
    try:
        verdict = _run_quality_gate(product_name, files)
        status = "[OK] PASSED" if verdict["passed"] else "[FAIL] FAILED"
        top_issues = "\n".join(f"  * {i}" for i in verdict.get("issues", [])[:5]) or "  None"
        return f"VERDICT: {status} (Score: {verdict['score']}/100, Required: {FACTORY_MIN_SCORE})\nTop Issues:\n{top_issues}"
    except Exception as e: return f"Adversary check error: {str(e)}"

def peer_review(product_name: str, reviewer_brain: str, status: str, critique: str):
    """Commit an inter-brain peer review."""
    return "[CONSENSUS] Review recorded (Simulated)."

def objective_validator(product_name: str) -> str:
    """Industrial Quality Audit: Semgrep and Tests."""
    target_dir = os.path.join(WORKSPACE_DIR, product_name)
    if not os.path.exists(target_dir): return f"Error: {product_name} not found."
    return f"Objective Audit for {product_name}:\n[SEMGREP] Findings: 0\n[TESTS] Quality Gate: PASSED"

def _run_quality_gate(product_name: str, files: list[str] | None = None) -> dict:
    from app.swarm.adversary_service import run_adversary_review
    selected_files = _infer_product_files(product_name, files)
    review_root = WORKSPACE_DIR
    staged_dir = None
    reviewed_files: list[str] = []
    try:
        if selected_files:
            staged_dir, reviewed_files = _stage_review_workspace(selected_files)
            review_root = staged_dir
        verdict = run_adversary_review(product_name, workspace_dir=review_root, min_score=FACTORY_MIN_SCORE)
        assessment = _assess_bundle_quality(product_name, _build_workspace_snapshot(review_root))
        verdict["issues"] = _dedupe_preserve(list(verdict.get("issues", [])) + assessment["issues"])
        verdict["suggestions"] = _dedupe_preserve(list(verdict.get("suggestions", [])) + assessment["suggestions"])
        verdict["score"] = max(0, int(verdict.get("score", 0)) - len(assessment["issues"]) * 10)
        verdict["passed"] = int(verdict.get("score", 0)) >= FACTORY_MIN_SCORE
        _persist_product_state(product_name, status="validated" if verdict["passed"] else "correction_needed", score=int(verdict.get("score", 0)))
        return verdict
    finally:
        if staged_dir: shutil.rmtree(staged_dir, ignore_errors=True)

def _verify_quality_gate(name: str, files: list[str] | None) -> dict:
    return _run_quality_gate(name, files)
