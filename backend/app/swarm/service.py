import asyncio
import datetime
import json
import logging
import os
import random
import re
import threading

from sqlalchemy.orm import Session

from app.config.service import NICHES, config_service
from app.core.paths import brain_log_path
from app.database.database import db_session as get_db
from app.swarm.governor import swarm_governor
from app.swarm.models import TaskQueue
from app.swarm.persona_engine import PersonaEngine
from app.swarm.repository import swarm_repo
from app.swarm.tools import execute_tool

logger = logging.getLogger("swarm_service")


class BrainInstance:
    def __init__(self, name: str, model: str, persona_type: str = "mimic"):
        self.name = name
        self.model = model
        self.persona_type = persona_type
        self.running = False
        self.log: list = []
        self.task_count = 0
        self.thread: threading.Thread | None = None
        self.engine = PersonaEngine(model=model)
        self.log_file = brain_log_path(name)
        self.current_phase = "idle"
        self.current_step = 0
        self.current_task_id: int | None = None
        self.last_tool: str | None = None
        self.last_error: str | None = None
        self.updated_at = datetime.datetime.utcnow().isoformat() + "Z"
        self.consecutive_failures = 0
        self.pause_seconds = 30
        self.state_file = self.log_file.with_name(f"{self.name.lower()}_state.json")
        self._load_state()
        self._load_log()

    def _load_state(self):
        if self.state_file.exists():
            try:
                with open(self.state_file, encoding="utf-8") as f:
                    state = json.load(f)
                    self.task_count = state.get("task_count", 0)
                    self.running = state.get("running", False)
                    self.current_task_id = state.get("current_task_id")
            except Exception as e:
                logger.warning(f"Failed to load state for {self.name}: {e}")

    def _save_state(self):
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "running": self.running,
                        "task_count": self.task_count,
                        "current_task_id": self.current_task_id,
                    },
                    f,
                )
        except Exception as e:
            logger.warning(f"Failed to save state for {self.name}: {e}")

    def _load_log(self):
        if self.log_file.exists():
            try:
                with open(self.log_file, encoding="utf-8") as f:
                    self.log = json.load(f)
                    logger.info(f"Loaded brain '{self.name}' log from persistence.")
            except Exception as e:
                logger.warning(f"Failed to load brain '{self.name}' log: {e}")
                self.log = []

    def save_log(self):
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(self.log[-100:], f)
        except Exception as e:
            logger.warning(f"Failed to save brain '{self.name}' log: {e}")

    def _append_log(self, role: str, content: str):
        self.log.append({"role": role, "content": content})
        self.save_log()

    def _set_progress(
        self,
        phase: str,
        detail: str | None = None,
        *,
        step: int | None = None,
        task_id: int | None = None,
        tool: str | None = None,
        error: str | None = None,
        log_event: bool = False,
    ):
        self.current_phase = phase
        if step is not None:
            self.current_step = step
        if task_id is not None or phase in {"idle", "stopped"}:
            self.current_task_id = task_id
        if tool is not None:
            self.last_tool = tool
        if error is not None:
            self.last_error = error
        elif phase not in {"error", "retrying"}:
            self.last_error = None
        self.updated_at = datetime.datetime.utcnow().isoformat() + "Z"
        if log_event and detail:
            self._append_log("system", f"[{phase.upper()}] {detail}")

    def _update_task_status(self, task_id: int | None, status: str):
        if task_id is None:
            return
        try:
            with get_db() as db:
                swarm_repo.update_task_status(db, task_id, status)
        except Exception as exc:
            logger.warning("Failed to mark task %s as %s: %s", task_id, status, exc)

    @staticmethod
    def _result_failed(result: str) -> bool:
        text = str(result).lower()
        return (
            text.startswith("error")
            or text.startswith("tool execution error")
            or "error:" in text
            or "error " in text
            or " blocked" in text
            or " failed" in text
        )

    @staticmethod
    def _safe_slug(value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", (value or "").strip().lower()).strip("_")
        return slug or "studio_app"

    async def _run_reverse_engineering_cycle(self, target_id: str, task_id: int) -> tuple[bool, str]:
        from app.reverse_engineering.schemas import SynthesisRequest
        from app.reverse_engineering.service import reverse_engineering_service

        cluster_id = reverse_engineering_service.resolve_default_cluster(target_id)
        req = SynthesisRequest(
            target=target_id,
            cluster_id=cluster_id,
            context=(
                f"Autonomous swarm mission #{task_id}.\n"
                f"Replicate one useful open-source agent capability for digital product production and app building.\n"
                f"Include structured runbook sections and production-ready code."
            ),
        )
        ok, status, job_id = await reverse_engineering_service.run_synthesis_async(req)
        if ok:
            return (
                True,
                f"Autonomous reverse engineering completed for '{target_id}' (job #{job_id}).",
            )
        return (
            False,
            f"Autonomous reverse engineering failed for '{target_id}' (job #{job_id}): {status}",
        )

    async def _run_strategic_cycle(
        self,
        niche: str,
        task_id: int,
        reverse_engineering_target: str | None = None,
    ) -> tuple[bool, str]:
        """
        LEVEL 6 INDUSTRIAL SWARM: LangGraph Orchestration + NATS Comms
        """
        self._append_log("system", f"[INDUSTRIAL-FLOW] Starting LangGraph cycle for '{niche}'...")

        if reverse_engineering_target:
            self._set_progress(
                "reverse_engineering",
                f"Autonomously reverse engineering target '{reverse_engineering_target}'.",
                task_id=task_id,
                log_event=True,
            )
            return await self._run_reverse_engineering_cycle(reverse_engineering_target, task_id)

        import asyncio

        from app.swarm.flow_manager import swarm_workflow
        from app.swarm.nats_service import nats_service

        # 1. Prepare Initial State
        initial_state = {
            "task_id": task_id,
            "product_name": f"{self.name.lower()}_optimized_{task_id}",
            "niche": niche,
            "specs": f"High-efficiency industrial tool for {niche}",
            "code_snapshot": {},
            "adversary_report": {},
            "attempts": 0,
            "max_attempts": 3,
            "status": "init",
        }

        # 2. Broadcast via NATS (Industrial Event)
        try:
            await nats_service.publish_task(
                "swarm.task.started", {"brain": self.name, "task_id": task_id, "niche": niche}
            )
        except Exception as e:
            logger.warning(f"NATS Telemetry skipped (Started): {e}")

        # 3. Execute Graph
        try:
            self._set_progress(
                "generating",
                f"Forging industrial solution for '{niche}'...",
                task_id=task_id,
                log_event=True,
            )

            # Running the compiled subgraph
            final_state = swarm_workflow.invoke(initial_state)

            self._set_progress(
                "auditing", "Adversary performing quality audit...", task_id=task_id, log_event=True
            )

            product_name = final_state["product_name"]
            if final_state["adversary_report"].get("passed"):
                self._set_progress(
                    "finalizing",
                    f"Publishing stable asset: {product_name}",
                    task_id=task_id,
                    log_event=True,
                )
                success_msg = f"LangGraph cycle success for '{product_name}'."
                try:
                    await nats_service.publish_task(
                        "swarm.task.completed", {"task_id": task_id, "product": product_name}
                    )
                except Exception as e:
                    logger.warning(f"NATS Telemetry skipped (Completed): {e}")
                return True, success_msg
            else:
                fail_reason = final_state["adversary_report"].get("raw", "Unknown failure")
                self._set_progress(
                    "fault_detected",
                    f"Audit failed: {fail_reason[:50]}",
                    task_id=task_id,
                    log_event=True,
                )
                try:
                    await nats_service.publish_task(
                        "swarm.task.failed", {"task_id": task_id, "reason": "Audit failed"}
                    )
                except Exception as e:
                    logger.warning(f"NATS Telemetry skipped (Failed): {e}")
                return False, f"Cycle halted: {fail_reason[:200]}"

        except Exception as e:
            logger.error(f"[FLOW-ERROR] LangGraph execution failed: {e}")
            return False, f"Orchestration fault: {str(e)}"

    def start(self, niche: str = ""):
        if self.running:
            return
        self.running = True
        self._save_state()
        self.engine.set_model(self.model)
        self._set_progress(
            "starting", f"Launching autonomous loop for {self.model}", task_id=None, log_event=True
        )

        # In a real async app, we'd use a Background Task manager or similar.
        # For now, we launch the async loop in the background.
        import asyncio

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._run_loop_async(niche))
        except RuntimeError:
            # Fallback if no loop is running (e.g. startup)
            threading.Thread(
                target=lambda: asyncio.run(self._run_loop_async(niche)), daemon=True
            ).start()

    def stop(self):
        self.running = False
        self._save_state()
        self._set_progress(
            "stopped", "Brain manually stopped.", step=0, task_id=None, log_event=True
        )

    async def _run_loop_async(self, niche: str):
        logger.info(f"Swarm Node Online: '{self.name}'")
        self._set_progress(
            "online", "Brain online and waiting for work.", step=0, task_id=None, log_event=True
        )

        while self.running:
            task = None
            try:
                with get_db() as db:
                    if not swarm_governor.check_token_limit(db, self.name):
                        self._set_progress(
                            "quota_locked",
                            "Daily token quota reached. Standing down.",
                            task_id=None,
                        )
                        await asyncio.sleep(600)
                        continue

                    task = self._acquire_task(db)
                    if not task:
                        task = self._discover_work(db)

                if task:
                    await self._execute_task_cycle(task)
            except Exception as e:
                logger.error(f"Swarm Fault - {self.name}: {e}")
                self._update_task_status(task.id if task else None, "correction_needed")
                self.consecutive_failures += 1
                self.pause_seconds = min(300, 30 * (2 ** min(self.consecutive_failures - 1, 3)))
                self._set_progress(
                    "error", str(e), task_id=task.id if task else None, error=str(e), log_event=True
                )

            await self._cooldown(task)

    def _acquire_task(self, db: Session) -> TaskQueue | None:
        if self.current_task_id:
            locked = swarm_repo.get_task(db, self.current_task_id)
            if locked and locked.status in {"running", "correction_needed"}:
                logger.info(
                    f"[FORGE-AUDIT] Brain '{self.name}' - Resuming LOCKED Task #{locked.id}"
                )
                return locked
            self.current_task_id = None

        repairs = swarm_repo.list_tasks_by_brain(db, self.name, "correction_needed")
        pending = swarm_repo.list_tasks_by_brain(db, self.name, "pending")
        return repairs[0] if repairs else (pending[0] if pending else None)

    def _discover_work(self, db: Session) -> TaskQueue:
        mission = swarm_governor.get_autonomous_mission_type(db)
        directive = getattr(swarm_manager, "global_directive", None)

        if directive:
            logger.warning(f"[FORGE-AUDIT] Brain '{self.name}' executing USER DIRECTIVE: {directive}")
            payload = {
                "niche": "User Directive",
                "goal": directive,
            }
            # Clear directive after one acquisition? Or keep it? 
            # Usually better to keep it until changed or cleared manually.
        elif mission == "reverse_engineering":
            target = swarm_governor.get_synthesis_target(db)
            logger.warning(
                f"[FORGE-AUDIT] Brain '{self.name}' activating Autonomous Synthesis: {target}"
            )
            payload = {
                "niche": "Reverse Engineering",
                "reverse_engineering_target": target,
                "goal": f"Reverse engineer agent target '{target}' into a reusable production tool.",
            }
        else:
            logger.warning(f"[FORGE-AUDIT] Brain '{self.name}' finds NO work. Forcing discovery...")
            self._set_progress(
                "hunting",
                "Scouting new market horizons...",
                step=0,
                tool="discover_new_niche",
                log_event=True,
            )
            target = execute_tool("discover_new_niche", {"depth": 5})
            execute_tool("add_to_global_niches", {"niche": target})
            payload = {"niche": target, "goal": "Autonomous Studio Expansion."}

        task = swarm_repo.create_task(db, self.name, "production", json.dumps(payload))
        self._set_progress("task_init", f"Mission: {target}.", task_id=task.id, log_event=True)
        return task

    async def _execute_task_cycle(self, task: TaskQueue):
        task_id = task.id
        with get_db() as db:
            swarm_repo.update_task_status(db, task_id, "running")

        self._set_progress(
            "task_running", f"Task #{task_id} running.", task_id=task_id, log_event=True
        )

        payload_dict = json.loads(task.payload) if task.payload else {}
        target_niche = payload_dict.get("niche") or random.choice(NICHES)

        cycle_ok, cycle_message = await self._run_strategic_cycle(
            target_niche,
            task_id,
            payload_dict.get("reverse_engineering_target"),
        )

        if not cycle_ok:
            raise RuntimeError(cycle_message)

        await self._finalize_task(task_id, cycle_message)

    async def _finalize_task(self, task_id: int, message: str):
        with get_db() as db:
            swarm_repo.update_task_status(db, task_id, "completed")
            swarm_governor.track_usage(db, self.name, tokens=random.randint(500, 2500))

        self._append_log("assistant", message)
        self.task_count += 1
        self.consecutive_failures = 0
        self.pause_seconds = 30
        self._save_state()
        self._set_progress(
            "completed", f"Task #{task_id} completed.", step=0, task_id=task_id, log_event=True
        )

    async def _cooldown(self, task: TaskQueue | None):
        wait_seconds = self.pause_seconds if task else max(60, self.pause_seconds)
        for _ in range(wait_seconds):
            if not self.running:
                break
            phase = "cooldown" if task else "idle"
            detail = f"Cooling down after task #{task.id}." if task else "Waiting for work."
            self._set_progress(phase, detail, step=0, task_id=task.id if task else None)
            await asyncio.sleep(1)


class SwarmManager:
    def __init__(self):
        self.brains: dict[str, BrainInstance] = {}
        default_model = os.getenv("CURRENT_MODEL", "qwen2.5:7b")
        # Initial industrial swarm setup
        self.spawn("MasterBrain", os.getenv("CURRENT_MODEL", "llama-3.3-70b-versatile"), "director")
        self.spawn("Dre", default_model, "coding")
        self.spawn("Fenko", default_model, "mimic")
        self.spawn("Codesmith", default_model, "coding")
        self.spawn("Ava", default_model, "reasoning")

        # Resume brains that were running before restart
        for brain in self.brains.values():
            if brain.running:
                brain.running = False
                brain.start()

        self.global_directive = None

    def set_directive(self, directive: str | None):
        self.global_directive = directive
        logger.info(f"[SWARM-DIRECTIVE] Global goal updated: {directive}")

    def spawn(self, name: str, model: str, persona_type: str = "mimic"):
        if name in self.brains:
            self.brains[name].model = model
            self.brains[name].persona_type = persona_type
            return self.brains[name]

        # --- CONCURRENCY CONSTRAINT (#6) ---
        with get_db() as db:
            max_brains_str = config_service.get_setting(db, "max_active_brains")
            max_brains = int(max_brains_str) if max_brains_str else 10

            active_count = sum(1 for b in self.brains.values() if b.running)
            if active_count >= max_brains:
                logger.warning(
                    f"[SWARM-SHED] Cannot spawn '{name}'. Max active brains ({max_brains}) reached."
                )
                return None

        brain = BrainInstance(name, model, persona_type)
        self.brains[name] = brain
        return brain

    def get_status(self):
        return {
            name: {
                "running": b.running,
                "tasks": b.task_count,
                "phase": b.current_phase,
                "step": b.current_step,
                "task_id": b.current_task_id,
                "last_tool": b.last_tool,
                "last_error": b.last_error,
                "model": b.model,
                "cloud": b.engine.is_cloud,
                "updated_at": b.updated_at,
                "last_log": b.log[-10:] if b.log else [],
            }
            for name, b in self.brains.items()
        }


swarm_manager = SwarmManager()
