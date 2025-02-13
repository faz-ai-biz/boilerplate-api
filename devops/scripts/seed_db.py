from src.core.security import get_password_hash
from src.db.models.user import User
from src.db.session import SessionLocal


def seed_database():
    """Seed database with initial data for development."""
    db = SessionLocal()
    test_users = [
        {"email": "admin@example.com", "password": "admin123"},
        {"email": "user@example.com", "password": "user123"},
    ]
    for user_data in test_users:
        if not db.query(User).filter(User.email == user_data["email"]).first():
            user = User(
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
            )
            db.add(user)
    db.commit()
    db.close()


if __name__ == "__main__":
    seed_database()
