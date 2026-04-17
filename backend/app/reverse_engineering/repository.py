import json

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

    def seed_builtin_targets(self, db: Session) -> None:
        existing = {target.target_id: target for target in db.query(AgentTarget).all()}
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

    def create_custom_target(self, db: Session, req: AgentTargetCreateRequest) -> AgentTarget:
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

    def list_targets(self, db: Session) -> list[AgentTarget]:
        return (
            db.query(AgentTarget)
            .order_by(AgentTarget.is_builtin.desc(), AgentTarget.name.asc())
            .all()
        )

    def get_target_by_id(self, db: Session, target_id: str) -> AgentTarget | None:
        normalized = self._normalize_key(target_id)
        if not normalized:
            return None
        return db.query(AgentTarget).filter(AgentTarget.target_id == normalized).first()

    def resolve_target(self, db: Session, raw_target: str) -> AgentTarget | None:
        normalized = self._normalize_key(raw_target)
        if not normalized:
            return None

        for target in self.list_targets(db):
            if normalized == self._normalize_key(target.target_id):
                return target
            if normalized == self._normalize_key(target.name):
                return target
            if normalized in {self._normalize_key(alias) for alias in target.aliases_list()}:
                return target
        return None

    def create_job(self, db: Session, req: SynthesisRequest) -> SynthesisJob:
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

    def get_job(self, db: Session, job_id: int) -> SynthesisJob | None:
        if job_id <= 0:
            return None
        return db.query(SynthesisJob).filter(SynthesisJob.id == job_id).first()

    def update_job_status(
        self,
        db: Session,
        job_id: int,
        status: str,
        result_code: str | None = None,
        purpose: str | None = None,
    ) -> SynthesisJob | None:
        job = self.get_job(db, job_id)
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

    def list_jobs_by_status(self, db: Session, status: str) -> list[SynthesisJob]:
        return db.query(SynthesisJob).filter(SynthesisJob.status == status).all()

    def list_all_jobs(self, db: Session) -> list[SynthesisJob]:
        return db.query(SynthesisJob).order_by(SynthesisJob.created_at.desc()).all()

    def create_replicated_tool(
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

    def list_replicated_tools(
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

    def get_replicated_tool(self, db: Session, tool_id: int) -> ReplicatedTool | None:
        if tool_id <= 0:
            return None
        return db.query(ReplicatedTool).filter(ReplicatedTool.id == tool_id).first()

    def list_replicated_tools_by_job(self, db: Session, job_id: int) -> list[ReplicatedTool]:
        if job_id <= 0:
            return []
        return (
            db.query(ReplicatedTool)
            .filter(ReplicatedTool.job_id == job_id)
            .order_by(ReplicatedTool.created_at.desc())
            .all()
        )


reverse_engineering_repo = ReverseEngineeringRepository()
