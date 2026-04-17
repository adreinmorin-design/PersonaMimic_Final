from sqlalchemy.orm import Session

from app.auth.models import Role, User


class AuthRepository:
    """
    Studio Standard Repository for authentication and authorization.
    Decouples Auth business logic from SQLAlchemy sessions.
    """

    def get_user_by_username(self, db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    def get_user_count(self, db: Session) -> int:
        return db.query(User).count()

    def get_role_by_name(self, db: Session, name: str) -> Role | None:
        return db.query(Role).filter(Role.name == name).first()

    def create_role(self, db: Session, name: str) -> Role:
        role = Role(name=name)
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    def create_user(self, db: Session, username: str, role_id: int) -> User:
        user = User(username=username, role_id=role_id)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


auth_repo = AuthRepository()
