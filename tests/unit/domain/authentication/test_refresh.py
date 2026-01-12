"""
Test for refresh
"""

import pytest

from src.domain.users import LoginService
from src.domain.users.services.login_services import UserToken
from src.domain.exceptions import SecurityError


from ...mock import MockUserRepository


@pytest.mark.asyncio
async def test_refresh_with_invalid_token(mock_user_repo: MockUserRepository):
    """
    Test refresh with invalid token
    """
    service = LoginService(mock_user_repo)
    with pytest.raises(SecurityError):
        await service.refresh_token("invalid-token")


@pytest.mark.asyncio
async def test_refresh_with_valid_token(
    mock_user_repo: MockUserRepository,
    get_jwt_tokens: UserToken,
):
    """
    Test refresh with valid token
    """
    service = LoginService(mock_user_repo)
    tokens = await service.refresh_token(get_jwt_tokens["refresh_token"])
    assert tokens
