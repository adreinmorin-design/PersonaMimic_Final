import asyncio

from sqlalchemy.orm import Session

from app.swarm.models import TaskQueue, UsageQuota


class SwarmRepository:
    """
    Studio Standard Repository for Swarm related persistence logic.
    Decouples business logic from SQLAlchemy sessions.
    """

    async def get_task(self, db: Session, task_id: int) -> TaskQueue | None:
        return await asyncio.to_thread(self._get_task_sync, db, task_id)

    def _get_task_sync(self, db: Session, task_id: int) -> TaskQueue | None:
        return db.query(TaskQueue).filter(TaskQueue.id == task_id).first()

    async def update_task_status(self, db: Session, task_id: int, status: str) -> None:
        await asyncio.to_thread(self._update_task_status_sync, db, task_id, status)

    def _update_task_status_sync(self, db: Session, task_id: int, status: str) -> None:
        db.query(TaskQueue).filter(TaskQueue.id == task_id).update({"status": status})
        db.commit()

    async def list_tasks_by_brain(
        self, db: Session, brain_name: str, status: str | None = None
    ) -> list[TaskQueue]:
        return await asyncio.to_thread(self._list_tasks_by_brain_sync, db, brain_name, status)

    def _list_tasks_by_brain_sync(
        self, db: Session, brain_name: str, status: str | None = None
    ) -> list[TaskQueue]:
        query = db.query(TaskQueue).filter(TaskQueue.brain_name == brain_name)
        if status:
            query = query.filter(TaskQueue.status == status)
        return query.all()

    async def create_task(
        self, db: Session, brain_name: str, task_type: str, payload: str
    ) -> TaskQueue:
        return await asyncio.to_thread(self._create_task_sync, db, brain_name, task_type, payload)

    def _create_task_sync(
        self, db: Session, brain_name: str, task_type: str, payload: str
    ) -> TaskQueue:
        task = TaskQueue(brain_name=brain_name, task_type=task_type, payload=payload)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    # Usage quota related methods
    async def get_quota(self, db: Session, brain_name: str, day: str) -> UsageQuota | None:
        return await asyncio.to_thread(self._get_quota_sync, db, brain_name, day)

    def _get_quota_sync(self, db: Session, brain_name: str, day: str) -> UsageQuota | None:
        return (
            db.query(UsageQuota)
            .filter(UsageQuota.brain_name == brain_name, UsageQuota.day == day)
            .first()
        )

    async def track_usage(self, db: Session, brain_name: str, day: str, tokens: int) -> None:
        await asyncio.to_thread(self._track_usage_sync, db, brain_name, day, tokens)

    def _track_usage_sync(self, db: Session, brain_name: str, day: str, tokens: int) -> None:
        quota = self._get_quota_sync(db, brain_name, day)
        if not quota:
            quota = UsageQuota(brain_name=brain_name, day=day, tokens_consumed=0, tasks_completed=0)
            db.add(quota)

        quota.tokens_consumed += tokens
        quota.tasks_completed += 1
        db.commit()


swarm_repo = SwarmRepository()
