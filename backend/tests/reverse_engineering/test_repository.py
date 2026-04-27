from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.reverse_engineering.repository import ReverseEngineeringRepository
from app.reverse_engineering.schemas import AgentTargetCreateRequest, SynthesisRequest


def _build_db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return Session()


def test_seed_builtin_targets_and_resolve_alias():
    db = _build_db_session()
    repo = ReverseEngineeringRepository()
    repo._seed_builtin_targets_sync(db)

    targets = repo._list_targets_sync(db)
    target_ids = {target.target_id for target in targets}
    assert "openhands" in target_ids
    assert "swe-agent" in target_ids

    resolved = repo._resolve_target_sync(db, "open hands")
    assert resolved is not None
    assert resolved.target_id == "openhands"


def test_create_custom_target_and_resolve():
    db = _build_db_session()
    repo = ReverseEngineeringRepository()
    repo._seed_builtin_targets_sync(db)

    created = repo._create_custom_target_sync(
        db,
        AgentTargetCreateRequest(
            target_id="my-agent",
            name="My Agent",
            description="Custom agent for app production.",
            source_repo_url="https://example.com/my-agent",
            aliases=["myagent", "my agent"],
        ),
    )
    assert created.target_id == "my-agent"
    resolved = repo._resolve_target_sync(db, "my agent")
    assert resolved is not None
    assert resolved.target_id == "my-agent"


def test_replicated_tool_round_trip_with_json_arrays():
    db = _build_db_session()
    repo = ReverseEngineeringRepository()
    repo._seed_builtin_targets_sync(db)

    tool = repo._create_replicated_tool_sync(
        db,
        job_id=55,
        target_id="openhands",
        target_name="OpenHands",
        tool_name="Pipeline Builder",
        source_repo_url="https://github.com/All-Hands-AI/OpenHands",
        status="completed",
        purpose_summary="Purpose",
        explanation="Explanation",
        prerequisites=["Python", "Docker"],
        setup_steps=["Install", "Configure"],
        run_steps=["Run"],
        integration_steps=["Hook into CI"],
        limitations=["Needs API key"],
        replicated_code="print('ok')",
    )

    fetched = repo._get_replicated_tool_sync(db, tool.id)
    assert fetched is not None
    assert fetched._decode_array(fetched.prerequisites) == ["Python", "Docker"]
    assert fetched._decode_array(fetched.setup_steps) == ["Install", "Configure"]


def test_get_job_metrics_by_status_returns_count_and_unique_targets():
    db = _build_db_session()
    repo = ReverseEngineeringRepository()

    repo._create_job_sync(
        db,
        SynthesisRequest(target="openhands", cluster_id="c_1", context="one"),
    )
    repo._create_job_sync(
        db,
        SynthesisRequest(target="openhands", cluster_id="c_2", context="two"),
    )
    repo._create_job_sync(
        db,
        SynthesisRequest(target="swe-agent", cluster_id="c_3", context="three"),
    )
    repo._update_job_status_sync(db, 1, "completed")
    repo._update_job_status_sync(db, 2, "completed")
    repo._update_job_status_sync(db, 3, "failed")

    metrics = repo._get_job_metrics_by_status_sync(db, "completed")

    assert metrics["job_count"] == 2
    assert metrics["capabilities"] == ["openhands"]
