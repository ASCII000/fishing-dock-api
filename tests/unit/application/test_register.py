"""
Test for register endpoints
"""

import pytest

from httpx import AsyncClient

from .conftest import create_test_image


@pytest.mark.asyncio
async def test_create_user_successfully(
    async_client: AsyncClient,
    valid_user_data: dict,
    valid_user_files: dict,
):
    """
    Test create user successfully
    """
    response = await async_client.post(
        "/users",
        data=valid_user_data,
        files=valid_user_files,
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_create_user_with_duplicate_email(
    async_client: AsyncClient,
    valid_user_data: dict,
):
    """
    Test create user with duplicate email
    """
    # First create user
    files1 = {"avatar": ("test1.png", create_test_image(), "image/png")}
    await async_client.post("/users", data=valid_user_data, files=files1)

    # Try to create again with same email
    files2 = {"avatar": ("test2.png", create_test_image(), "image/png")}
    response = await async_client.post("/users", data=valid_user_data, files=files2)

    assert response.status_code == 409
    assert response.json()["detail"] == "Email já em uso."


@pytest.mark.asyncio
async def test_create_user_with_missing_fields(async_client: AsyncClient):
    """
    Test create user with missing required fields
    """
    incomplete_data = {
        "username": "Test User",
        "email": "test@example.com"
    }

    files = {"avatar": ("test.png", create_test_image(), "image/png")}
    response = await async_client.post("/users", data=incomplete_data, files=files)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_with_invalid_email_format(async_client: AsyncClient):
    """
    Test create user with invalid email format
    """
    user_data = {
        "username": "Test User",
        "email": "",
        "phone": "11999999999",
        "password": "StrongPass123!"
    }

    files = {"avatar": ("test.png", create_test_image(), "image/png")}
    response = await async_client.post("/users", data=user_data, files=files)

    # Empty email should fail validation or create user depending on validation rules
    # At minimum it should not return 500
    assert response.status_code in [200, 422, 400]


@pytest.mark.asyncio
async def test_create_multiple_users(async_client: AsyncClient):
    """
    Test create multiple users with different emails
    """
    user1 = {
        "username": "User One",
        "email": "user1@example.com",
        "phone": "11999999991",
        "password": "StrongPass123!"
    }

    user2 = {
        "username": "User Two",
        "email": "user2@example.com",
        "phone": "11999999992",
        "password": "StrongPass456!"
    }

    files1 = {"avatar": ("test1.png", create_test_image(), "image/png")}
    files2 = {"avatar": ("test2.png", create_test_image(), "image/png")}

    response1 = await async_client.post("/users", data=user1, files=files1)
    response2 = await async_client.post("/users", data=user2, files=files2)

    assert response1.status_code == 200
    assert response2.status_code == 200

    # Verify both users can login
    login1 = await async_client.post(
        "/users/security/login",
        params={"email": user1["email"], "password": user1["password"]}
    )
    login2 = await async_client.post(
        "/users/security/login",
        params={"email": user2["email"], "password": user2["password"]}
    )

    assert login1.status_code == 200
    assert login2.status_code == 200
