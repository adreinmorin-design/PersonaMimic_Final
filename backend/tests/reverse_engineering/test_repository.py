from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.reverse_engineering.repository import ReverseEngineeringRepository
from app.reverse_engineering.schemas import AgentTargetCreateRequest


def _build_db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return Session()


def test_seed_builtin_targets_and_resolve_alias():
    db = _build_db_session()
    repo = ReverseEngineeringRepository()
    repo.seed_builtin_targets(db)

    targets = repo.list_targets(db)
    target_ids = {target.target_id for target in targets}
    assert "openhands" in target_ids
    assert "swe-agent" in target_ids

    resolved = repo.resolve_target(db, "open hands")
    assert resolved is not None
    assert resolved.target_id == "openhands"


def test_create_custom_target_and_resolve():
    db = _build_db_session()
    repo = ReverseEngineeringRepository()
    repo.seed_builtin_targets(db)

    created = repo.create_custom_target(
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
    resolved = repo.resolve_target(db, "my agent")
    assert resolved is not None
    assert resolved.target_id == "my-agent"


def test_replicated_tool_round_trip_with_json_arrays():
    db = _build_db_session()
    repo = ReverseEngineeringRepository()
    repo.seed_builtin_targets(db)

    tool = repo.create_replicated_tool(
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

    fetched = repo.get_replicated_tool(db, tool.id)
    assert fetched is not None
    assert fetched._decode_array(fetched.prerequisites) == ["Python", "Docker"]
    assert fetched._decode_array(fetched.setup_steps) == ["Install", "Configure"]
