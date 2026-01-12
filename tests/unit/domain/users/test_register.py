"""
Tests for user register
"""

import pytest

from src.domain.users import RegisterService
from src.domain.exceptions import DuplicateException
from src.domain.entities.user import UserEntity

from ...mock import MockUserRepository
from ...mock.mock_users import NOT_EXISTENT_EMAIL


@pytest.mark.asyncio
async def test_create_valid_user(
    mock_user_repo: MockUserRepository,
    mock_user_not_existent: UserEntity,
):
    """
    Test create user
    """
    service = RegisterService(mock_user_repo)
    user = await service.create_new_user(mock_user_not_existent)
    assert user.email == NOT_EXISTENT_EMAIL


@pytest.mark.asyncio
async def test_create_user_already_exists(
    mock_user_repo: MockUserRepository,
    mock_existent_user_entity: UserEntity,
):
    """
    Test create user
    """
    service = RegisterService(mock_user_repo)
    with pytest.raises(DuplicateException):
        await service.create_new_user(mock_existent_user_entity)
