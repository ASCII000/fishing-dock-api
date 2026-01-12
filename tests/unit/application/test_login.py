"""
Test for login endpoints
"""

import pytest

from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_with_valid_credentials(async_client: AsyncClient, valid_user_data: dict):
    """
    Test login with valid credentials
    """
    # First create user
    await async_client.post("/users", json=valid_user_data)

    # Then login
    response = await async_client.post(
        "/users/security/login",
        params={
            "email": valid_user_data["email"],
            "password": valid_user_data["senha"]
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_with_invalid_email(async_client: AsyncClient):
    """
    Test login with non existent email
    """
    response = await async_client.post(
        "/users/security/login",
        params={
            "email": "nonexistent@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email ou senha incorretos."


@pytest.mark.asyncio
async def test_login_with_invalid_password(async_client: AsyncClient, valid_user_data: dict):
    """
    Test login with invalid password
    """
    # First create user
    await async_client.post("/users", json=valid_user_data)

    # Then try login with wrong password
    response = await async_client.post(
        "/users/security/login",
        params={
            "email": valid_user_data["email"],
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email ou senha incorretos."


@pytest.mark.asyncio
async def test_refresh_token_with_valid_token(async_client: AsyncClient, valid_user_data: dict):
    """
    Test refresh token with valid token
    """
    # First create user and login
    await async_client.post("/users", json=valid_user_data)

    login_response = await async_client.post(
        "/users/security/login",
        params={
            "email": valid_user_data["email"],
            "password": valid_user_data["senha"]
        }
    )

    tokens = login_response.json()

    # Then refresh token
    response = await async_client.get(
        "/users/security/refresh",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_token_with_invalid_token(async_client: AsyncClient):
    """
    Test refresh token with invalid token
    """
    response = await async_client.get(
        "/users/security/refresh",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_without_token(async_client: AsyncClient):
    """
    Test refresh token without authorization header
    """
    response = await async_client.get("/users/security/refresh")

    # HTTPBearer returns 401 when no authorization header is provided
    assert response.status_code == 401
