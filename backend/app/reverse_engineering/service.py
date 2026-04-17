import asyncio
import json
import logging
import re
from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.database.database import db_session
from app.reverse_engineering.models import AgentTarget, ReplicatedTool
from app.reverse_engineering.repository import reverse_engineering_repo
from app.reverse_engineering.schemas import AgentTargetCreateRequest, SynthesisRequest
from app.swarm.synthesis_agent import synthesis_agent

logger = logging.getLogger("reverse_engineering_service")


class ReverseEngineeringService:
    CONTRACT_LABELS = {
        "TOOL_NAME": "tool_name",
        "PURPOSE_SUMMARY": "purpose_summary",
        "EXPLANATION": "explanation",
        "PREREQUISITES[]": "prerequisites",
        "PREREQUISITES": "prerequisites",
        "SETUP_STEPS[]": "setup_steps",
        "SETUP_STEPS": "setup_steps",
        "RUN_STEPS[]": "run_steps",
        "RUN_STEPS": "run_steps",
        "INTEGRATION_STEPS[]": "integration_steps",
        "INTEGRATION_STEPS": "integration_steps",
        "LIMITATIONS[]": "limitations",
        "LIMITATIONS": "limitations",
        "CODE": "code",
    }
    REQUIRED_FIELDS = (
        "tool_name",
        "purpose_summary",
        "explanation",
        "prerequisites",
        "setup_steps",
        "run_steps",
        "integration_steps",
        "limitations",
        "code",
    )
    PLACEHOLDER_PATTERNS = (
        re.compile(r"\bTODO\b", re.IGNORECASE),
        re.compile(r"\bpass\b"),
        re.compile(r"raise\s+NotImplementedError", re.IGNORECASE),
        re.compile(r"\bPLACEHOLDER\b", re.IGNORECASE),
    )
    # BEST OF TOOL MAPPING: Prioritizing Studio Grade Engineering Agents
    TARGET_CLUSTER_MAP = {
        "openhands": "c_104",  # General Engineering & Orchestration
        "devika": "c_104",  # Planning & Goal Decomposition
        "swe-agent": "c_882",  # Complex Logic & Deep Bug Resolution
        "crewai": "c_104",
        "metagpt": "c_882",
        "autogpt": "c_882",
        "superagi": "c_104",
        "gpt-engineer": "c_104",
    }

    @staticmethod
    def _log_background_result(task: asyncio.Task) -> None:
        try:
            task.result()
        except Exception:
            logger.exception("Reverse engineering background task crashed.")

    @classmethod
    def serialize_target(cls, target: AgentTarget) -> dict:
        return {
            "id": target.id,
            "target_id": target.target_id,
            "name": target.name,
            "description": target.description,
            "source_repo_url": target.source_repo_url,
            "aliases": target.aliases_list(),
            "is_builtin": bool(target.is_builtin),
            "created_at": target.created_at,
        }

    @classmethod
    def serialize_tool(cls, tool: ReplicatedTool) -> dict:
        return {
            "id": tool.id,
            "job_id": tool.job_id,
            "target_id": tool.target_id,
            "target_name": tool.target_name,
            "tool_name": tool.tool_name,
            "source_repo_url": tool.source_repo_url,
            "status": tool.status,
            "purpose_summary": tool.purpose_summary,
            "explanation": tool.explanation,
            "prerequisites": tool._decode_array(tool.prerequisites),
            "setup_steps": tool._decode_array(tool.setup_steps),
            "run_steps": tool._decode_array(tool.run_steps),
            "integration_steps": tool._decode_array(tool.integration_steps),
            "limitations": tool._decode_array(tool.limitations),
            "replicated_code": tool.replicated_code,
            "created_at": tool.created_at,
        }

    @staticmethod
    def _clean_list_items(items: Iterable[str]) -> list[str]:
        cleaned: list[str] = []
        for item in items:
            text = str(item).strip()
            text = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", text)
            if text:
                cleaned.append(text)
        return cleaned

    @classmethod
    def _parse_list_section(cls, raw: str) -> list[str]:
        raw = (raw or "").strip()
        if not raw:
            return []

        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return cls._clean_list_items([str(item) for item in parsed])
        except Exception:
            pass

        lines = [line for line in raw.splitlines() if line.strip()]
        if not lines and raw:
            lines = [raw]

        if len(lines) == 1 and ";" in lines[0]:
            lines = [segment for segment in lines[0].split(";") if segment.strip()]
        return cls._clean_list_items(lines)

    @classmethod
    def _parse_contract_sections(cls, content: str) -> dict[str, object]:
        sections: dict[str, list[str]] = {}
        current_field: str | None = None
        normalized = (content or "").replace("\r\n", "\n")

        for line in normalized.split("\n"):
            match = re.match(r"^\s*([A-Z_]+(?:\[\])?)\s*:\s*(.*)$", line)
            if match:
                label = match.group(1).strip().upper()
                mapped = cls.CONTRACT_LABELS.get(label)
                if mapped:
                    current_field = mapped
                    sections.setdefault(current_field, [])
                    initial_value = match.group(2).strip()
                    if initial_value:
                        sections[current_field].append(initial_value)
                    continue
            if current_field:
                sections.setdefault(current_field, [])
                sections[current_field].append(line)

        parsed: dict[str, object] = {
            "tool_name": "",
            "purpose_summary": "",
            "explanation": "",
            "prerequisites": [],
            "setup_steps": [],
            "run_steps": [],
            "integration_steps": [],
            "limitations": [],
            "code": "",
        }
        for key, values in sections.items():
            body = "\n".join(values).strip()
            if key in {
                "prerequisites",
                "setup_steps",
                "run_steps",
                "integration_steps",
                "limitations",
            }:
                parsed[key] = cls._parse_list_section(body)
            else:
                parsed[key] = body
        return parsed

    @classmethod
    def _contains_placeholder_patterns(cls, text: str) -> bool:
        payload = text or ""
        return any(pattern.search(payload) for pattern in cls.PLACEHOLDER_PATTERNS)

    @classmethod
    def _build_runbook_payload(cls, synthesis_result: dict[str, object]) -> dict[str, object]:
        raw_content = str(
            synthesis_result.get("raw_content") or synthesis_result.get("content") or ""
        )
        parsed = cls._parse_contract_sections(raw_content)

        payload = cls._initialize_payload(synthesis_result, parsed)
        payload["raw_content"] = raw_content

        cls._finalize_payload_lists(payload)
        cls._validate_payload_completeness(payload)

        return payload

    @classmethod
    def _initialize_payload(cls, result: dict, parsed: dict) -> dict:
        code = str(result.get("code") or parsed["code"] or "")
        purpose = str(
            result.get("purpose_summary")
            or result.get("purpose")
            or parsed["purpose_summary"]
            or ""
        )
        explanation = str(result.get("explanation") or parsed["explanation"] or "")
        name = str(result.get("tool_name") or parsed["tool_name"] or "Replicated Tool").strip()

        return {
            "tool_name": name,
            "purpose_summary": purpose,
            "explanation": explanation,
            "prerequisites": result.get("prerequisites") or parsed["prerequisites"],
            "setup_steps": result.get("setup_steps") or parsed["setup_steps"],
            "run_steps": result.get("run_steps") or parsed["run_steps"],
            "integration_steps": result.get("integration_steps") or parsed["integration_steps"],
            "limitations": result.get("limitations") or parsed["limitations"],
            "code": code,
        }

    @classmethod
    def _finalize_payload_lists(cls, payload: dict):
        list_keys = (
            "prerequisites",
            "setup_steps",
            "run_steps",
            "integration_steps",
            "limitations",
        )
        for key in list_keys:
            val = payload[key]
            if isinstance(val, list):
                payload[key] = cls._clean_list_items(val)
            elif isinstance(val, str):
                payload[key] = cls._parse_list_section(val)
            else:
                payload[key] = []

    @classmethod
    def _validate_payload_completeness(cls, payload: dict):
        missing = [
            f
            for f in cls.REQUIRED_FIELDS
            if not str(payload[f]).strip() or (isinstance(payload[f], list) and not payload[f])
        ]
        payload["status"] = "partial" if missing else "completed"
        payload["missing_required"] = missing

        if cls._contains_placeholder_patterns(
            payload["code"]
        ) or cls._contains_placeholder_patterns(payload["raw_content"]):
            payload["status"] = "flagged"

    def create_custom_target(
        self, db: Session, target_request: AgentTargetCreateRequest
    ) -> AgentTarget:
        return reverse_engineering_repo.create_custom_target(db, target_request)

    def list_targets(self, db: Session) -> list[AgentTarget]:
        return reverse_engineering_repo.list_targets(db)

    @classmethod
    def resolve_default_cluster(cls, target_id: str) -> str:
        return cls.TARGET_CLUSTER_MAP.get((target_id or "").strip().lower(), "c_104")

    def trigger_synthesis(self, db: Session, req: SynthesisRequest):
        resolved_target = reverse_engineering_repo.resolve_target(db, req.target)
        if not resolved_target:
            logger.error("Unsupported synthesis target: %s", req.target)
            return None

        normalized_req = SynthesisRequest(
            target=resolved_target.target_id,
            cluster_id=req.cluster_id.strip(),
            context=req.context,
            purpose=req.purpose,
        )
        job = reverse_engineering_repo.create_job(db, normalized_req)

        try:
            task = asyncio.create_task(
                self._process_job(
                    job.id,
                    normalized_req,
                    resolved_target.target_id,
                    resolved_target.name,
                    resolved_target.source_repo_url,
                )
            )
            task.add_done_callback(self._log_background_result)
        except RuntimeError:
            logger.exception("No running event loop; unable to schedule reverse engineering job.")
            reverse_engineering_repo.update_job_status(db, job.id, "failed")

        return job

    async def run_synthesis_async(self, req: SynthesisRequest) -> tuple[bool, str, int | None]:
        """
        Runs reverse engineering asynchronously within an existing event loop.
        """
        with db_session() as db:
            resolved_target = reverse_engineering_repo.resolve_target(db, req.target)
            if not resolved_target:
                return False, f"Unsupported synthesis target: {req.target}", None

            target_id = resolved_target.target_id
            target_name = resolved_target.name
            source_repo_url = resolved_target.source_repo_url

            cluster_id = req.cluster_id.strip() or self.resolve_default_cluster(target_id)
            normalized_req = SynthesisRequest(
                target=target_id,
                cluster_id=cluster_id,
                context=req.context,
                purpose=req.purpose,
            )
            job = reverse_engineering_repo.create_job(db, normalized_req)

        try:
            await self._process_job(
                job.id,
                normalized_req,
                target_id,
                target_name,
                source_repo_url,
            )
        except Exception as exc:
            logger.error("Async reverse engineering failed for job %s: %s", job.id, exc)
            with db_session() as db:
                reverse_engineering_repo.update_job_status(db, job.id, "failed")
            return False, str(exc), job.id

        with db_session() as db:
            finished = reverse_engineering_repo.get_job(db, job.id)
            if not finished:
                return False, "Synthesis job disappeared unexpectedly.", job.id
            success = finished.status == "completed"
            return success, finished.status, job.id

    def run_synthesis_inline(self, req: SynthesisRequest) -> tuple[bool, str, int | None]:
        """
        Runs reverse engineering synchronously. Use only if NO event loop is available.
        """
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                logger.warning("run_synthesis_inline called from running loop. Logic should be awaited instead.")
                # This is a fallback but shouldn't be relied upon; caller should be async
                return False, "Called from running loop. Use run_synthesis_async instead.", None
        except RuntimeError:
            pass

        with db_session() as db:
            resolved_target = reverse_engineering_repo.resolve_target(db, req.target)
            if not resolved_target:
                return False, f"Unsupported synthesis target: {req.target}", None

            target_id = resolved_target.target_id
            target_name = resolved_target.name
            source_repo_url = resolved_target.source_repo_url

            cluster_id = req.cluster_id.strip() or self.resolve_default_cluster(target_id)
            normalized_req = SynthesisRequest(
                target=target_id,
                cluster_id=cluster_id,
                context=req.context,
                purpose=req.purpose,
            )
            job = reverse_engineering_repo.create_job(db, normalized_req)

        try:
            asyncio.run(
                self._process_job(
                    job.id,
                    normalized_req,
                    target_id,
                    target_name,
                    source_repo_url,
                )
            )
        except Exception as exc:
            logger.error("Inline reverse engineering failed for job %s: %s", job.id, exc)
            with db_session() as db:
                reverse_engineering_repo.update_job_status(db, job.id, "failed")
            return False, str(exc), job.id

        with db_session() as db:
            finished = reverse_engineering_repo.get_job(db, job.id)
            if not finished:
                return False, "Synthesis job disappeared unexpectedly.", job.id
            success = finished.status == "completed"
            return success, finished.status, job.id

    async def _process_job(
        self,
        job_id: int,
        req: SynthesisRequest,
        target_id: str,
        target_name: str,
        source_repo_url: str | None,
    ):
        try:
            logger.info("Starting reverse engineering for %s (Job: %s)", req.target, job_id)
            self._update_job_status(job_id, "processing")

            result = await self._synthesize_tool(req, target_id, target_name, source_repo_url)
            runbook = self._build_runbook_payload(result)

            self._finalize_job_record(job_id, target_id, target_name, source_repo_url, runbook)

            logger.info("Finished job %s (status=%s)", job_id, runbook["status"])
        except Exception as exc:
            logger.error("Job %s failed: %s", job_id, exc)
            self._update_job_status(job_id, "failed")

    def _update_job_status(
        self, job_id: int, status: str, code: str | None = None, purpose: str | None = None
    ):
        with db_session() as db:
            reverse_engineering_repo.update_job_status(db, job_id, status, code, purpose)

    async def _synthesize_tool(
        self, req: SynthesisRequest, target_id: str, name: str, url: str | None
    ) -> dict:
        context = f"TARGET: {name} ({target_id})\nSOURCE: {url or 'n/a'}\nCONTEXT: {req.context}"
        return await asyncio.to_thread(
            synthesis_agent.synthesize_from_cluster, req.cluster_id, context
        )

    def _finalize_job_record(
        self, job_id: int, target_id: str, name: str, url: str | None, runbook: dict
    ):
        with db_session() as db:
            reverse_engineering_repo.create_replicated_tool(
                db,
                job_id=job_id,
                target_id=target_id,
                target_name=name,
                tool_name=str(runbook["tool_name"]),
                source_repo_url=url,
                status=str(runbook["status"]),
                replicated_code=str(runbook.get("code")),
                purpose_summary=str(runbook.get("purpose_summary")),
                explanation=str(runbook.get("explanation")),
                prerequisites=list(runbook.get("prerequisites", [])),
                setup_steps=list(runbook.get("setup_steps", [])),
                run_steps=list(runbook.get("run_steps", [])),
                integration_steps=list(runbook.get("integration_steps", [])),
                limitations=list(runbook.get("limitations", [])),
            )

            final_status = "failed" if runbook["status"] == "flagged" else "completed"
            reverse_engineering_repo.update_job_status(
                db,
                job_id,
                final_status,
                str(runbook.get("code")),
                str(runbook.get("purpose_summary")),
            )


reverse_engineering_service = ReverseEngineeringService()
