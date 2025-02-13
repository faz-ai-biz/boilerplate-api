import pytest
from fastapi.testclient import TestClient


def test_auth_flow_integration(client, test_db):
    """Test complete authentication flow"""
    # 1. Register new user
    register_response = client.post(
        "/api/v1/users",
        json={"email": "integration@example.com", "password": "IntegrationTest123!"},
    )
    assert register_response.status_code == 200

    # 2. Login with new user
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "integration@example.com", "password": "IntegrationTest123!"},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]

    # 3. Access protected resource
    protected_response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert protected_response.status_code == 200
    assert protected_response.json()["email"] == "integration@example.com"

    # 4. Refresh token
    refresh_response = client.post(
        "/api/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert refresh_response.status_code == 200
    new_access_token = refresh_response.json()["access_token"]

    # 5. Use new access token
    new_protected_response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {new_access_token}"}
    )
    assert new_protected_response.status_code == 200


def test_concurrent_sessions(client, test_db):
    """Test handling of multiple sessions for the same user"""
    # Register user
    client.post(
        "/api/v1/users",
        json={"email": "concurrent@example.com", "password": "ConcurrentTest123!"},
    )

    # Login multiple times
    sessions = []
    for _ in range(3):
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "concurrent@example.com",
                "password": "ConcurrentTest123!",
            },
        )
        assert response.status_code == 200
        sessions.append(response.json()["access_token"])

    # Verify all sessions are valid
    for token in sessions:
        response = client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


def test_invalid_token_handling(client):
    """Test how the system handles various invalid token scenarios"""
    endpoints = [
        "/api/v1/users/me",
        "/api/v1/auth/protected",
    ]

    invalid_tokens = [
        "totally.invalid.token",
        "invalid.token.format",
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid",
        "",
        "Bearer ",
    ]

    for endpoint in endpoints:
        for invalid_token in invalid_tokens:
            response = client.get(
                endpoint, headers={"Authorization": f"Bearer {invalid_token}"}
            )
            assert response.status_code in [401, 422]
