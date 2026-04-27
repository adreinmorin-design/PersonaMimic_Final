import asyncio
import json

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.reverse_engineering.catalog import BUILTIN_AGENT_TARGETS
from app.reverse_engineering.models import AgentTarget, ReplicatedTool, SynthesisJob
from app.reverse_engineering.schemas import AgentTargetCreateRequest, SynthesisRequest


class ReverseEngineeringRepository:
    @staticmethod
    def _normalize_key(raw: str) -> str:
        return (raw or "").strip().lower()

    @staticmethod
    def _serialize_array(items: list[str] | None) -> str:
        clean = [item.strip() for item in (items or []) if item and item.strip()]
        return json.dumps(clean)

    async def seed_builtin_targets(self, db: Session) -> None:
        await asyncio.to_thread(self._seed_builtin_targets_sync, db)

    def _seed_builtin_targets_sync(self, db: Session) -> None:
        builtin_ids = [str(item["target_id"]) for item in BUILTIN_AGENT_TARGETS]
        existing = {
            target.target_id: target
            for target in db.query(AgentTarget)
            .filter(AgentTarget.target_id.in_(builtin_ids))
            .all()
        }
        for item in BUILTIN_AGENT_TARGETS:
            target_id = str(item["target_id"])
            row = existing.get(target_id)
            payload = {
                "name": str(item["name"]),
                "description": str(item.get("description", "")) or None,
                "source_repo_url": str(item.get("source_repo_url", "")) or None,
                "aliases": self._serialize_array([str(alias) for alias in item.get("aliases", [])]),
                "is_builtin": True,
            }
            if row:
                row.name = payload["name"]
                row.description = payload["description"]
                row.source_repo_url = payload["source_repo_url"]
                row.aliases = payload["aliases"]
                row.is_builtin = True
            else:
                db.add(AgentTarget(target_id=target_id, **payload))
        db.commit()

    async def create_custom_target(self, db: Session, req: AgentTargetCreateRequest) -> AgentTarget:
        return await asyncio.to_thread(self._create_custom_target_sync, db, req)

    def _create_custom_target_sync(self, db: Session, req: AgentTargetCreateRequest) -> AgentTarget:
        target_id = self._normalize_key(req.target_id)
        if not target_id:
            raise ValueError("target_id is required")

        existing = db.query(AgentTarget).filter(AgentTarget.target_id == target_id).first()
        if existing:
            raise ValueError(f"Target '{target_id}' already exists.")

        aliases = [self._normalize_key(alias) for alias in req.aliases]
        aliases = [alias for alias in aliases if alias and alias != target_id]

        target = AgentTarget(
            target_id=target_id,
            name=req.name.strip(),
            description=req.description.strip() if req.description else None,
            source_repo_url=req.source_repo_url.strip() if req.source_repo_url else None,
            aliases=self._serialize_array(aliases),
            is_builtin=False,
        )
        db.add(target)
        db.commit()
        db.refresh(target)
        return target

    async def list_targets(self, db: Session) -> list[AgentTarget]:
        return await asyncio.to_thread(self._list_targets_sync, db)

    def _list_targets_sync(self, db: Session) -> list[AgentTarget]:
        return (
            db.query(AgentTarget)
            .order_by(AgentTarget.is_builtin.desc(), AgentTarget.name.asc())
            .all()
        )

    async def get_target_by_id(self, db: Session, target_id: str) -> AgentTarget | None:
        return await asyncio.to_thread(self._get_target_by_id_sync, db, target_id)

    def _get_target_by_id_sync(self, db: Session, target_id: str) -> AgentTarget | None:
        normalized = self._normalize_key(target_id)
        if not normalized:
            return None
        return db.query(AgentTarget).filter(AgentTarget.target_id == normalized).first()

    async def resolve_target(self, db: Session, raw_target: str) -> AgentTarget | None:
        return await asyncio.to_thread(self._resolve_target_sync, db, raw_target)

    def _resolve_target_sync(self, db: Session, raw_target: str) -> AgentTarget | None:
        normalized = self._normalize_key(raw_target)
        if not normalized:
            return None

        normalized_name = func.lower(func.trim(AgentTarget.name))
        target = (
            db.query(AgentTarget)
            .filter(or_(AgentTarget.target_id == normalized, normalized_name == normalized))
            .order_by(AgentTarget.is_builtin.desc(), AgentTarget.name.asc())
            .first()
        )
        if target:
            return target

        likely_alias_matches = (
            db.query(AgentTarget)
            .filter(AgentTarget.aliases.contains(normalized))
            .order_by(AgentTarget.is_builtin.desc(), AgentTarget.name.asc())
            .all()
        )
        for target in likely_alias_matches:
            if normalized == self._normalize_key(target.target_id):
                return target
            if normalized == self._normalize_key(target.name):
                return target
            if normalized in {self._normalize_key(alias) for alias in target.aliases_list()}:
                return target
        return None

    async def create_job(self, db: Session, req: SynthesisRequest) -> SynthesisJob:
        return await asyncio.to_thread(self._create_job_sync, db, req)

    def _create_job_sync(self, db: Session, req: SynthesisRequest) -> SynthesisJob:
        target = req.target.strip()
        cluster_id = req.cluster_id.strip()
        if not target or not cluster_id:
            raise ValueError("Target and cluster_id are required.")

        job = SynthesisJob(
            target=target,
            cluster_id=cluster_id,
            context=req.context,
            purpose=req.purpose,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    async def get_job(self, db: Session, job_id: int) -> SynthesisJob | None:
        return await asyncio.to_thread(self._get_job_sync, job_id, db)

    def _get_job_sync(self, job_id: int, db: Session) -> SynthesisJob | None:
        if job_id <= 0:
            return None
        return db.query(SynthesisJob).filter(SynthesisJob.id == job_id).first()

    async def update_job_status(
        self,
        db: Session,
        job_id: int,
        status: str,
        result_code: str | None = None,
        purpose: str | None = None,
    ) -> SynthesisJob | None:
        return await asyncio.to_thread(
            self._update_job_status_sync, db, job_id, status, result_code, purpose
        )

    def _update_job_status_sync(
        self,
        db: Session,
        job_id: int,
        status: str,
        result_code: str | None = None,
        purpose: str | None = None,
    ) -> SynthesisJob | None:
        job = self._get_job_sync(job_id, db)
        if not job:
            return None

        job.status = status
        if result_code is not None:
            job.result_code = result_code
        if purpose is not None:
            job.purpose = purpose

        db.commit()
        db.refresh(job)
        return job

    async def list_jobs_by_status(self, db: Session, status: str) -> list[SynthesisJob]:
        return await asyncio.to_thread(self._list_jobs_by_status_sync, db, status)

    def _list_jobs_by_status_sync(self, db: Session, status: str) -> list[SynthesisJob]:
        return db.query(SynthesisJob).filter(SynthesisJob.status == status).all()

    async def get_job_metrics_by_status(self, db: Session, status: str) -> dict[str, object]:
        return await asyncio.to_thread(self._get_job_metrics_by_status_sync, db, status)

    def _get_job_metrics_by_status_sync(self, db: Session, status: str) -> dict[str, object]:
        normalized_status = self._normalize_key(status)
        base_query = db.query(SynthesisJob).filter(SynthesisJob.status == normalized_status)
        job_count = base_query.count()
        capabilities = [
            target
            for (target,) in (
                db.query(SynthesisJob.target)
                .filter(SynthesisJob.status == normalized_status, SynthesisJob.target.isnot(None))
                .distinct()
                .all()
            )
            if target
        ]
        return {"job_count": job_count, "capabilities": capabilities}

    async def list_all_jobs(self, db: Session) -> list[SynthesisJob]:
        return await asyncio.to_thread(self._list_all_jobs_sync, db)

    def _list_all_jobs_sync(self, db: Session) -> list[SynthesisJob]:
        return db.query(SynthesisJob).order_by(SynthesisJob.created_at.desc()).all()

    async def create_replicated_tool(
        self,
        db: Session,
        **kwargs,
    ) -> ReplicatedTool:
        return await asyncio.to_thread(self._create_replicated_tool_sync, db, **kwargs)

    def _create_replicated_tool_sync(
        self,
        db: Session,
        *,
        job_id: int,
        target_id: str,
        target_name: str,
        tool_name: str,
        source_repo_url: str | None,
        status: str,
        purpose_summary: str | None,
        explanation: str | None,
        prerequisites: list[str] | None,
        setup_steps: list[str] | None,
        run_steps: list[str] | None,
        integration_steps: list[str] | None,
        limitations: list[str] | None,
        replicated_code: str | None,
    ) -> ReplicatedTool:
        tool = ReplicatedTool(
            job_id=job_id,
            target_id=target_id,
            target_name=target_name,
            tool_name=tool_name.strip() or "Replicated Tool",
            source_repo_url=source_repo_url,
            status=status,
            purpose_summary=purpose_summary,
            explanation=explanation,
            prerequisites=self._serialize_array(prerequisites),
            setup_steps=self._serialize_array(setup_steps),
            run_steps=self._serialize_array(run_steps),
            integration_steps=self._serialize_array(integration_steps),
            limitations=self._serialize_array(limitations),
            replicated_code=replicated_code,
        )
        db.add(tool)
        db.commit()
        db.refresh(tool)
        return tool

    async def list_replicated_tools(
        self,
        db: Session,
        *,
        target_id: str | None = None,
        status: str | None = None,
    ) -> list[ReplicatedTool]:
        return await asyncio.to_thread(
            self._list_replicated_tools_sync, db, target_id=target_id, status=status
        )

    def _list_replicated_tools_sync(
        self,
        db: Session,
        *,
        target_id: str | None = None,
        status: str | None = None,
    ) -> list[ReplicatedTool]:
        query = db.query(ReplicatedTool)
        if target_id:
            query = query.filter(ReplicatedTool.target_id == self._normalize_key(target_id))
        if status:
            query = query.filter(ReplicatedTool.status == self._normalize_key(status))
        return query.order_by(ReplicatedTool.created_at.desc()).all()

    async def get_replicated_tool(self, db: Session, tool_id: int) -> ReplicatedTool | None:
        return await asyncio.to_thread(self._get_replicated_tool_sync, db, tool_id)

    def _get_replicated_tool_sync(self, db: Session, tool_id: int) -> ReplicatedTool | None:
        if tool_id <= 0:
            return None
        return db.query(ReplicatedTool).filter(ReplicatedTool.id == tool_id).first()

    async def list_replicated_tools_by_job(self, db: Session, job_id: int) -> list[ReplicatedTool]:
        return await asyncio.to_thread(self._list_replicated_tools_by_job_sync, db, job_id)

    def _list_replicated_tools_by_job_sync(self, db: Session, job_id: int) -> list[ReplicatedTool]:
        if job_id <= 0:
            return []
        return (
            db.query(ReplicatedTool)
            .filter(ReplicatedTool.job_id == job_id)
            .order_by(ReplicatedTool.created_at.desc())
            .all()
        )


reverse_engineering_repo = ReverseEngineeringRepository()
