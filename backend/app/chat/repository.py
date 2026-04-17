from sqlalchemy.orm import Session

from app.chat.models import InteractionLog


class ChatRepository:
    """
    Studio Standard Repository for chat persistence.
    Decouples Chat business logic from SQLAlchemy sessions.
    """

    def log_interaction(
        self, db: Session, user_id: int, message: str, response: str
    ) -> InteractionLog:
        log = InteractionLog(user_id=user_id, message=message, response=response)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    def list_user_logs(self, db: Session, user_id: int) -> list[InteractionLog]:
        return (
            db.query(InteractionLog)
            .filter(InteractionLog.user_id == user_id)
            .order_by(InteractionLog.timestamp.desc())
            .all()
        )


chat_repo = ChatRepository()
