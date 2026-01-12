"""
Test for login
"""

import pytest

from src.domain.users import LoginService
from src.domain.exceptions import SecurityError


from ...mock import MockUserRepository
from ...mock.mock_users import NOT_EXISTENT_EMAIL, USER_PASSWORD



@pytest.mark.asyncio
async def test_login_not_existent_user(mock_user_repo: MockUserRepository):
    """
    Test login not existent user
    """
    service = LoginService(mock_user_repo)
    with pytest.raises(SecurityError):
        await service.login(NOT_EXISTENT_EMAIL, "password")


@pytest.mark.asyncio
async def test_login_user(mock_user_repo: MockUserRepository):
    """
    Test login user
    """
    service = LoginService(mock_user_repo)
    user = await service.login("email@existent-mock", USER_PASSWORD)
    assert user


@pytest.mark.asyncio
async def test_login_with_invalid_password(mock_user_repo: MockUserRepository):
    """
    Test login with invalid password
    """
    service = LoginService(mock_user_repo)
    with pytest.raises(SecurityError):
        await service.login("email@existent-mock", "invalid-password")
