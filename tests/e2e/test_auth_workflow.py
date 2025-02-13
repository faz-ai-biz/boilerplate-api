import time

import pytest
from fastapi.testclient import TestClient


def test_complete_auth_workflow(client, test_db):
    """Test the complete authentication workflow from registration to logout."""

    # 1. Register new user
    register_data = {"email": "e2e@example.com", "password": "E2ETest123!"}
    register_response = client.post("/api/v1/users", json=register_data)
    assert register_response.status_code == 200, register_response.text

    # 2. Attempt login with wrong password
    wrong_login_response = client.post(
        "/api/v1/auth/login",
        data={"username": register_data["email"], "password": "WrongPassword123!"},
    )
    assert wrong_login_response.status_code == 401, wrong_login_response.text

    # 3. Login with correct credentials
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": register_data["email"],
            "password": register_data["password"],
        },
    )
    assert login_response.status_code == 200, login_response.text
    tokens = login_response.json()
    assert "access_token" in tokens and "refresh_token" in tokens

    # 4. Access protected resources
    me_response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_response.status_code == 200, me_response.text
    assert me_response.json()["email"] == register_data["email"]

    # 5. Refresh token
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
    )
    assert refresh_response.status_code == 200, refresh_response.text
    new_tokens = refresh_response.json()
    assert "access_token" in new_tokens

    # 6. Verify old token is invalidated (with retries for race condition handling)
    time.sleep(1)  # Give backend time to invalidate
    for _ in range(3):
        old_token_response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        if old_token_response.status_code == 401:
            break
        time.sleep(1)
    assert old_token_response.status_code == 401, old_token_response.text

    # 7. Use new token
    new_me_response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
    )
    assert new_me_response.status_code == 200, new_me_response.text

    # 8. Logout
    logout_response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
    )
    assert logout_response.status_code == 200, logout_response.text

    # 9. Verify logged-out token is invalid (with retries)
    time.sleep(1)
    for _ in range(3):
        final_response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
        )
        if final_response.status_code == 401:
            break
        time.sleep(1)
    assert final_response.status_code == 401, final_response.text
