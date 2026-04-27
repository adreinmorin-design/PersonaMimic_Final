import asyncio
import importlib
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, patch


def test_get_intelligence_uses_metrics_snapshot():
    fake_cache_module = ModuleType("app.core.cache")
    fake_cache_module.cache = SimpleNamespace(_enabled=False)

    fake_repo_module = ModuleType("app.reverse_engineering.repository")
    fake_repo_module.reverse_engineering_repo = SimpleNamespace(
        get_job_metrics_by_status=AsyncMock(
            return_value={
                "job_count": 7,
                "capabilities": ["crewai", "openhands", "crewai"],
            }
        )
    )

    fake_swarm_module = ModuleType("app.swarm.service")
    fake_swarm_module.swarm_manager = SimpleNamespace(
        brains={
            "Dre": SimpleNamespace(running=True),
            "Fenko": SimpleNamespace(running=False),
            "Codesmith": SimpleNamespace(running=True),
        }
    )

    with patch.dict(
        sys.modules,
        {
            "app.core.cache": fake_cache_module,
            "app.reverse_engineering.repository": fake_repo_module,
            "app.swarm.service": fake_swarm_module,
        },
    ):
        sys.modules.pop("app.system.service", None)
        service_module = importlib.import_module("app.system.service")
        payload = asyncio.run(service_module.system_service.get_intelligence(SimpleNamespace()))

    fake_repo_module.reverse_engineering_repo.get_job_metrics_by_status.assert_awaited_once()
    assert payload["job_count"] == 7
    assert payload["capabilities"] == ["crewai", "openhands"]
    assert payload["active_brains"] == 2
    assert payload["tier"] == 1
