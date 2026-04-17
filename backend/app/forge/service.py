"""
app/forge/service.py - Autonomous Forge Orchestrator
The 'Mind' that monitors swarm failures and applies neural corrections.
"""

import logging

from app.forge.diagnostic import diagnostic_suite
from app.forge.repository import forge_repo
from app.forge.steering import INDUSTRIAL_STEERING_COLLECTION, steer_service
from app.forge.training import forge_worker

logger = logging.getLogger("forge.service")


class ForgeOrchestrator:
    def __init__(self):
        self.auto_steering_enabled = True

    def autonomous_correction(
        self, brain_name: str, task_id: int, error_message: str, file_context: str | None = None
    ) -> bool:
        """Log failure and apply neural steering if possible."""
        logger.info(f"[FORGE-MIND] Analyzing failure for {brain_name} (Task #{task_id})...")
        forge_repo.log_failure(brain_name, task_id, error_message)

        # 1. Diagnostic Audit
        if diagnostic_suite.benchmark_memory()["status"] == "CRITICAL":
            logger.warning("[FORGE-MIND] Memory pressure detected. Triggering layer-offloading...")

        # 2. Mechanistic Analysis
        if not self._is_placeholder_failure(error_message):
            return False

        if self.auto_steering_enabled:
            return self._apply_completeness_steering()

        return False

    @staticmethod
    def _is_placeholder_failure(error: str) -> bool:
        return any(x in error.lower() for x in ["placeholder", "todo"])

    def _apply_completeness_steering(self) -> bool:
        logger.info(
            "[FORGE-MIND] Placeholder usage detected! Activating 'code_completeness' steering vector..."
        )
        steer_service.add_vector(
            name="code_completeness",
            layer=INDUSTRIAL_STEERING_COLLECTION["code_completeness"]["layer"],
            vector_data=INDUSTRIAL_STEERING_COLLECTION["code_completeness"]["vector"],
            coefficient=1.2,
        )
        return True

    def check_fine_tuning_readiness(self, successful_tasks_count: int) -> bool:
        """Automatically trigger a forge session when enough 'Gold Data' exists."""
        if successful_tasks_count < 100:
            return False

        logger.info(
            "[FORGE-MIND] Studio-Grade threshold reached (100 products). Triggering Autonomous Fine-Tuning..."
        )
        from app.core.paths import DATABASE_PATH

        dataset = forge_worker.prepare_dataset(DATABASE_PATH)
        forge_worker.trigger_training(dataset)
        return True


# Singleton instance
forge_service = ForgeOrchestrator()
