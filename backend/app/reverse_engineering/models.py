import datetime
import json

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.database.database import Base


class SynthesisJob(Base):
    __tablename__ = "synthesis_jobs"
    id = Column(Integer, primary_key=True, index=True)
    target = Column(String, index=True)  # e.g. "phoenix", "appsmith"
    cluster_id = Column(String)
    context = Column(Text)
    status = Column(String, default="pending")
    result_code = Column(Text, nullable=True)
    purpose = Column(Text, nullable=True)  # Description of what the tool does and its importance
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AgentTarget(Base):
    __tablename__ = "agent_targets"
    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    source_repo_url = Column(String, nullable=True)
    aliases = Column(Text, default="[]")  # JSON array payload
    is_builtin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def aliases_list(self) -> list[str]:
        try:
            parsed = json.loads(self.aliases or "[]")
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except Exception:
            return []
        return []


class ReplicatedTool(Base):
    __tablename__ = "replicated_tools"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, index=True, nullable=False)
    target_id = Column(String, index=True, nullable=False)
    target_name = Column(String, nullable=False)
    tool_name = Column(String, nullable=False)
    source_repo_url = Column(String, nullable=True)
    status = Column(String, default="completed", index=True)
    purpose_summary = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    prerequisites = Column(Text, default="[]")  # JSON array payload
    setup_steps = Column(Text, default="[]")  # JSON array payload
    run_steps = Column(Text, default="[]")  # JSON array payload
    integration_steps = Column(Text, default="[]")  # JSON array payload
    limitations = Column(Text, default="[]")  # JSON array payload
    replicated_code = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def _decode_array(raw_value: str | None) -> list[str]:
        if not raw_value:
            return []
        try:
            parsed = json.loads(raw_value)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except Exception:
            return []
        return []
