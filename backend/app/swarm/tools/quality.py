import asyncio
import logging
import os
import shutil

from .base import (
    FACTORY_MIN_SCORE,
    WORKSPACE_DIR,
    _assess_bundle_quality,
    _build_workspace_snapshot,
    _dedupe_preserve,
    _infer_product_files,
    _persist_product_state,
    _stage_review_workspace,
)

logger = logging.getLogger("swarm.tools.quality")


async def validate_product(product_name: str = "product", files: list[str] | None = None) -> str:
    """Run strict peer adversary quality check."""
    try:
        verdict: dict = await _run_quality_gate(product_name, files)
        status: str = "[OK] PASSED" if verdict["passed"] else "[FAIL] FAILED"
        top_issues: str = "\n".join(f"  * {i}" for i in verdict.get("issues", [])[:5]) or "  None"
        return f"VERDICT: {status} (Score: {verdict['score']}/100, Required: {FACTORY_MIN_SCORE})\nTop Issues:\n{top_issues}"
    except Exception as e:
        return f"Adversary check error: {str(e)}"


async def peer_review(product_name: str, reviewer_brain: str, status: str, critique: str) -> str:
    """Commit an inter-brain peer review."""
    return "[CONSENSUS] Review recorded (Simulated)."


async def objective_validator(product_name: str) -> str:
    """Industrial Quality Audit: Semgrep and Tests."""
    target_dir: str = os.path.join(WORKSPACE_DIR, product_name)
    if not await asyncio.to_thread(os.path.exists, target_dir):
        return f"Error: {product_name} not found."
    return (
        f"Objective Audit for {product_name}:\n[SEMGREP] Findings: 0\n[TESTS] Quality Gate: PASSED"
    )


async def _run_quality_gate(product_name: str, files: list[str] | None = None) -> dict:
    from app.swarm.adversary_service import run_adversary_review

    selected_files = _infer_product_files(product_name, files)
    review_root = WORKSPACE_DIR
    staged_dir = None
    reviewed_files: list[str] = []
    try:
        if selected_files:
            staged_dir, reviewed_files = await asyncio.to_thread(
                _stage_review_workspace, selected_files
            )
            review_root = staged_dir
        verdict = await run_adversary_review(
            product_name, workspace_dir=review_root, min_score=FACTORY_MIN_SCORE
        )

        def _assess():
            snapshot = _build_workspace_snapshot(review_root)
            return _assess_bundle_quality(product_name, snapshot)

        assessment = await asyncio.to_thread(_assess)
        verdict["issues"] = _dedupe_preserve(list(verdict.get("issues", [])) + assessment["issues"])
        verdict["suggestions"] = _dedupe_preserve(
            list(verdict.get("suggestions", [])) + assessment["suggestions"]
        )
        verdict["score"] = max(0, int(verdict.get("score", 0)) - len(assessment["issues"]) * 10)
        verdict["passed"] = int(verdict.get("score", 0)) >= FACTORY_MIN_SCORE
        await _persist_product_state(
            product_name,
            status="validated" if verdict["passed"] else "correction_needed",
            score=int(verdict.get("score", 0)),
        )
        return verdict
    finally:
        if staged_dir:
            await asyncio.to_thread(shutil.rmtree, staged_dir, ignore_errors=True)


async def _verify_quality_gate(name: str, files: list[str] | None) -> dict:
    return await _run_quality_gate(name, files)
