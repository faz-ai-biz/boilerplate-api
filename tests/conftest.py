import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.core.token_manager import create_access_token
from src.db.models import Base
from src.db.session import get_db
from src.main import app


@pytest.fixture
def auth_headers():
    """Create authentication headers with test token"""
    access_token, _ = create_access_token(
        {
            "user_id": 1,
            "type": "access",
            "aud": "test-audience",  # Explicitly set test audience
        }
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_user_data():
    """Test user credentials"""
    return {"email": "test@example.com", "password": "TestPass123"}


@pytest.fixture
def test_db():
    """Create test database and tables"""
    test_engine = create_engine(settings.TEST_DATABASE_URL)
    TestingSessionLocal = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield TestingSessionLocal
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(test_db):
    """Create test client with database session"""

    def override_get_db():
        try:
            db = test_db()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setattr(settings, "ENVIRONMENT", "test")
    monkeypatch.setattr(settings, "TOKEN_AUDIENCE", "test-audience")
    yield
