import asyncio

from sqlalchemy.orm import Session

from app.chat.models import InteractionLog


class ChatRepository:
    """
    Studio Standard Repository for chat persistence.
    Decouples Chat business logic from SQLAlchemy sessions.
    """

    async def log_interaction(
        self, db: Session, user_id: int, message: str, response: str
    ) -> InteractionLog:
        return await asyncio.to_thread(self._log_interaction_sync, db, user_id, message, response)

    def _log_interaction_sync(
        self, db: Session, user_id: int, message: str, response: str
    ) -> InteractionLog:
        log = InteractionLog(user_id=user_id, message=message, response=response)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    async def list_user_logs(self, db: Session, user_id: int) -> list[InteractionLog]:
        return await asyncio.to_thread(self._list_user_logs_sync, db, user_id)

    def _list_user_logs_sync(self, db: Session, user_id: int) -> list[InteractionLog]:
        return (
            db.query(InteractionLog)
            .filter(InteractionLog.user_id == user_id)
            .order_by(InteractionLog.timestamp.desc())
            .all()
        )


chat_repo = ChatRepository()
