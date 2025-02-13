from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from src.core.security import get_password_hash
from src.core.token_manager import create_access_token
from src.db.models.user import User


def test_auth_endpoints():
    # Placeholder for auth endpoints unit tests
    assert True, "Implement auth endpoints unit tests here."


def test_login_success(client, test_db):
    """Test successful login attempt"""
    # Setup test user
    db = test_db()
    test_user = User(
        email="test@example.com", hashed_password=get_password_hash("TestPass123")
    )
    db.add(test_user)
    db.commit()

    # Test login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "TestPass123"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "wrong@example.com", "password": "WrongPass123"},
    )

    assert response.status_code == 401
    assert "detail" in response.json()


def test_refresh_token(client, test_db):
    """Test token refresh functionality"""
    # Setup test user
    db = test_db()
    test_user = User(
        email="refresh@example.com", hashed_password=get_password_hash("TestPass123")
    )
    db.add(test_user)
    db.commit()

    # Get initial tokens
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "refresh@example.com", "password": "TestPass123"},
    )
    refresh_token = response.json()["refresh_token"]

    # Test refresh
    response = client.post(
        "/api/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_protected_route(client):
    """Test protected route access"""
    # Create a test token - properly unpack the tuple
    token_str, _ = create_access_token(
        {"user_id": 1}
    )  # Changed from 'sub' to 'user_id'

    # Test with valid token
    response = client.get(
        "/api/v1/auth/protected", headers={"Authorization": f"Bearer {token_str}"}
    )
    assert response.status_code == 200

    # Test without token
    response = client.get("/api/v1/auth/protected")
    assert response.status_code == 401

    # Test with invalid token
    response = client.get(
        "/api/v1/auth/protected", headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


def test_access_token_invalidation_after_refresh(client, test_db):
    """Test that old access token is invalidated after refresh"""
    # Setup test user
    db = test_db()
    test_user = User(
        email="invalidation@example.com",
        hashed_password=get_password_hash("TestPass123"),
    )
    db.add(test_user)
    db.commit()

    # Login to get tokens
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "invalidation@example.com", "password": "TestPass123"},
    )
    old_access_token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]

    # Verify old access token works
    me_response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {old_access_token}"}
    )
    assert me_response.status_code == 200

    # Refresh token
    refresh_response = client.post(
        "/api/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert refresh_response.status_code == 200

    # Verify old access token is now invalid
    me_response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {old_access_token}"}
    )
    assert me_response.status_code == 401
