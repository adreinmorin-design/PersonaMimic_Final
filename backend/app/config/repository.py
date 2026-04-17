from sqlalchemy.orm import Session

from app.config.models import Keystroke, SystemSetting


class ConfigRepository:
    """
    Studio Standard Repository for system configuration and keystroke analytics.
    Decouples Config business logic from SQLAlchemy sessions.
    """

    def get_setting(self, db: Session, key: str) -> SystemSetting | None:
        return db.query(SystemSetting).filter(SystemSetting.key == key).first()

    def update_setting(
        self, db: Session, key: str, value: str, is_encrypted: bool = False
    ) -> SystemSetting:
        setting = self.get_setting(db, key)
        if not setting:
            setting = SystemSetting(key=key)
            db.add(setting)

        setting.value = value
        setting.is_encrypted = is_encrypted
        db.commit()
        db.refresh(setting)
        return setting

    def list_settings(self, db: Session) -> list[SystemSetting]:
        return db.query(SystemSetting).all()

    def create_keystroke(self, db: Session, user_id: int, data: str) -> Keystroke:
        keystroke = Keystroke(user_id=user_id, data=data)
        db.add(keystroke)
        db.commit()
        db.refresh(keystroke)
        return keystroke


config_repo = ConfigRepository()
