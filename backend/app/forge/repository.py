from typing import Any
import logging

logger = logging.getLogger("forge.repository")


class ForgeRepository:
    """
    Studio Standard Repository for Forge related data.
    Manages failure history and neural correction state.
    """

    def __init__(self):
        self._failure_history: list[dict[str, Any]] = []

    def log_failure(self, brain_name: str, task_id: int, error_message: str) -> dict[str, Any]:
        failure_event = {
            "brain": brain_name,
            "task_id": task_id,
            "error": error_message,
        }
        self._failure_history.append(failure_event)
        return failure_event

    def get_failure_history(self) -> list[dict[str, Any]]:
        return self._failure_history

    def get_failure_count(self) -> int:
        return len(self._failure_history)


forge_repo = ForgeRepository()
