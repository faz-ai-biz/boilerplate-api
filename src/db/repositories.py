from sqlalchemy.orm import Session

from src.core.security import get_password_hash
from src.db.models.user import User


def create_user_repo(db_session: Session, email: str, password: str):
    try:
        existing = db_session.query(User).filter(User.email == email).first()
        if existing:
            return None

        hashed_password = get_password_hash(password)
        db_user = User(email=email, hashed_password=hashed_password)
        db_session.add(db_user)
        db_session.commit()
        db_session.refresh(db_user)
        return db_user
    except Exception:
        db_session.rollback()
        raise


def get_user_repo(db_session: Session, user_id: int):
    """Get user by ID from the database."""
    return db_session.query(User).filter(User.id == user_id).first()


def get_user_by_email(db_session: Session, email: str):
    return db_session.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, hashed_password: str) -> User:
    """Create a new user."""
    db_user = User(email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
