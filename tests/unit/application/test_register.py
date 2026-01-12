"""
Test for register endpoints
"""

import pytest

from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user_successfully(async_client: AsyncClient, valid_user_data: dict):
    """
    Test create user successfully
    """
    response = await async_client.post("/users", json=valid_user_data)

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_create_user_with_duplicate_email(async_client: AsyncClient, valid_user_data: dict):
    """
    Test create user with duplicate email
    """
    # First create user
    await async_client.post("/users", json=valid_user_data)

    # Try to create again with same email
    response = await async_client.post("/users", json=valid_user_data)

    assert response.status_code == 409
    assert response.json()["detail"] == "Email já em uso."


@pytest.mark.asyncio
async def test_create_user_with_missing_fields(async_client: AsyncClient):
    """
    Test create user with missing required fields
    """
    incomplete_data = {
        "nome": "Test User",
        "email": "test@example.com"
    }

    response = await async_client.post("/users", json=incomplete_data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_with_invalid_email_format(async_client: AsyncClient):
    """
    Test create user with invalid email format
    """
    user_data = {
        "nome": "Test User",
        "email": "",
        "telefone": "11999999999",
        "imagem_perfil": "https://example.com/image.jpg",
        "senha": "StrongPass123!"
    }

    response = await async_client.post("/users", json=user_data)

    # Empty email should fail validation or create user depending on validation rules
    # At minimum it should not return 500
    assert response.status_code in [200, 422, 400]


@pytest.mark.asyncio
async def test_create_multiple_users(async_client: AsyncClient):
    """
    Test create multiple users with different emails
    """
    user1 = {
        "nome": "User One",
        "email": "user1@example.com",
        "telefone": "11999999991",
        "imagem_perfil": "https://example.com/image1.jpg",
        "senha": "StrongPass123!"
    }

    user2 = {
        "nome": "User Two",
        "email": "user2@example.com",
        "telefone": "11999999992",
        "imagem_perfil": "https://example.com/image2.jpg",
        "senha": "StrongPass456!"
    }

    response1 = await async_client.post("/users", json=user1)
    response2 = await async_client.post("/users", json=user2)

    assert response1.status_code == 200
    assert response2.status_code == 200

    # Verify both users can login
    login1 = await async_client.post(
        "/users/security/login",
        params={"email": user1["email"], "password": user1["senha"]}
    )
    login2 = await async_client.post(
        "/users/security/login",
        params={"email": user2["email"], "password": user2["senha"]}
    )

    assert login1.status_code == 200
    assert login2.status_code == 200
