import asyncio
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

import pytest

from app.reverse_engineering.schemas import SynthesisRequest
from app.reverse_engineering.service import ReverseEngineeringService


@pytest.fixture
def service():
    return ReverseEngineeringService()


@pytest.fixture
def mock_db():
    return MagicMock()


def _fake_target():
    return SimpleNamespace(
        target_id="openhands",
        name="OpenHands",
        source_repo_url="https://github.com/All-Hands-AI/OpenHands",
    )


@patch("app.reverse_engineering.service.reverse_engineering_repo")
def test_trigger_synthesis_invalid_target(mock_repo, service, mock_db):
    req = SynthesisRequest(target="invalid", cluster_id="c_123", context="test")
    mock_repo.resolve_target.return_value = None
    job = service.trigger_synthesis(mock_db, req)
    assert job is None
    mock_repo.create_job.assert_not_called()


@patch("app.reverse_engineering.service.reverse_engineering_repo")
def test_trigger_synthesis_valid_target(mock_repo, service, mock_db):
    req = SynthesisRequest(target="OpenHands", cluster_id="c_123", context="test")
    mock_job = MagicMock()
    mock_job.id = 1
    mock_repo.resolve_target.return_value = _fake_target()
    mock_repo.create_job.return_value = mock_job

    def fake_create_task(coro):
        coro.close()
        task = MagicMock()
        task.add_done_callback = MagicMock()
        return task

    with patch(
        "app.reverse_engineering.service.asyncio.create_task", side_effect=fake_create_task
    ) as mock_create_task:
        job = service.trigger_synthesis(mock_db, req)

    assert job == mock_job
    created_req = mock_repo.create_job.call_args.args[1]
    assert created_req.target == "openhands"
    assert created_req.cluster_id == "c_123"
    mock_create_task.assert_called_once()


def test_parse_runbook_strict_contract(service):
    raw = """
TOOL_NAME: Deploy Helper
PURPOSE_SUMMARY: Speeds up deployment.
EXPLANATION: Automates packaging and deployment workflows.
PREREQUISITES[]:
- Python 3.11
- Docker
SETUP_STEPS[]:
1. Install deps
2. Configure env
RUN_STEPS[]:
1. Execute runner
INTEGRATION_STEPS[]:
1. Add CI hook
LIMITATIONS[]:
- Requires network access
CODE:
def run():
    return "ok"
""".strip()

    parsed = service._build_runbook_payload({"raw_content": raw})

    assert parsed["status"] == "completed"
    assert parsed["tool_name"] == "Deploy Helper"
    assert parsed["prerequisites"] == ["Python 3.11", "Docker"]
    assert "def run()" in parsed["code"]


def test_parse_runbook_partial_when_missing_sections(service):
    raw = """
TOOL_NAME: Thin Tool
EXPLANATION: Minimal output
CODE:
print("hello")
""".strip()

    parsed = service._build_runbook_payload({"raw_content": raw})

    assert parsed["status"] == "partial"
    assert "run_steps" in parsed["missing_required"]


def test_parse_runbook_flagged_for_placeholders(service):
    parsed = service._build_runbook_payload(
        {
            "tool_name": "Bad Tool",
            "purpose_summary": "bad",
            "explanation": "bad",
            "prerequisites": ["A"],
            "setup_steps": ["B"],
            "run_steps": ["C"],
            "integration_steps": ["D"],
            "limitations": ["E"],
            "code": "def run():\n    pass",
        }
    )
    assert parsed["status"] == "flagged"


@patch("app.reverse_engineering.service.reverse_engineering_repo")
@patch("app.reverse_engineering.service.synthesis_agent")
def test_process_job_success_creates_tool(mock_agent, mock_repo, service, mock_db):
    req = SynthesisRequest(target="openhands", cluster_id="c_123", context="test")
    mock_agent.synthesize_from_cluster.return_value = {
        "tool_name": "Builder",
        "purpose_summary": "purpose",
        "explanation": "explain",
        "prerequisites": ["git"],
        "setup_steps": ["install"],
        "run_steps": ["run"],
        "integration_steps": ["integrate"],
        "limitations": ["limit"],
        "code": "print('ok')",
        "raw_content": "CODE: print('ok')",
    }

    @contextmanager
    def fake_db_session():
        yield mock_db

    with patch("app.reverse_engineering.service.db_session", side_effect=lambda: fake_db_session()):
        asyncio.run(
            service._process_job(
                7,
                req,
                target_id="openhands",
                target_name="OpenHands",
                source_repo_url="https://github.com/All-Hands-AI/OpenHands",
            )
        )

    mock_repo.update_job_status.assert_has_calls(
        [
            call(mock_db, 7, "processing"),
            call(mock_db, 7, "completed", "print('ok')", "purpose"),
        ]
    )
    mock_repo.create_replicated_tool.assert_called_once()


@patch("app.reverse_engineering.service.reverse_engineering_repo")
@patch("app.reverse_engineering.service.synthesis_agent")
def test_process_job_flagged_marks_failed(mock_agent, mock_repo, service, mock_db):
    req = SynthesisRequest(target="openhands", cluster_id="c_123", context="test")
    mock_agent.synthesize_from_cluster.return_value = {
        "tool_name": "Flagged",
        "purpose_summary": "purpose",
        "explanation": "explain",
        "prerequisites": ["git"],
        "setup_steps": ["install"],
        "run_steps": ["run"],
        "integration_steps": ["integrate"],
        "limitations": ["limit"],
        "code": "def broken():\n    pass",
    }

    @contextmanager
    def fake_db_session():
        yield mock_db

    with patch("app.reverse_engineering.service.db_session", side_effect=lambda: fake_db_session()):
        asyncio.run(
            service._process_job(
                9,
                req,
                target_id="openhands",
                target_name="OpenHands",
                source_repo_url=None,
            )
        )

    mock_repo.update_job_status.assert_has_calls(
        [
            call(mock_db, 9, "processing"),
            call(mock_db, 9, "failed", "def broken():\n    pass", "purpose"),
        ]
    )
    mock_repo.create_replicated_tool.assert_called_once()


@patch("app.reverse_engineering.service.reverse_engineering_repo")
@patch("app.reverse_engineering.service.synthesis_agent")
def test_process_job_failure(mock_agent, mock_repo, service, mock_db):
    req = SynthesisRequest(target="openhands", cluster_id="c_123", context="test")
    mock_agent.synthesize_from_cluster.side_effect = RuntimeError("boom")

    @contextmanager
    def fake_db_session():
        yield mock_db

    with patch("app.reverse_engineering.service.db_session", side_effect=lambda: fake_db_session()):
        asyncio.run(
            service._process_job(
                8,
                req,
                target_id="openhands",
                target_name="OpenHands",
                source_repo_url=None,
            )
        )

    mock_repo.update_job_status.assert_has_calls(
        [
            call(mock_db, 8, "processing"),
            call(mock_db, 8, "failed"),
        ]
    )
