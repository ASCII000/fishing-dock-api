# pylint: disable=redefined-outer-name

"""
Configuration for pytest
"""

import pytest
import pytest_asyncio

from src.domain.entities import UserEntity
from src.domain.users import LoginService
from .unit.mock import MockUserRepository
from .unit.mock.mock_users import NOT_EXISTENT_EMAIL, NOT_EXISTENT_UUID, USER_PASSWORD


@pytest.fixture(scope='session')
def mock_user_repo():
    """
    Mock user repository
    """
    return MockUserRepository()


@pytest.fixture(scope='session')
def mock_existent_user_entity():
    """
    Mock user entity existent
    """
    return UserEntity(
        email="email@existent-mock",
        nome="Luiz Souza",
        telefone="11999999999",
        uuid="uuid",
        imagem_perfil=None,
        ativo=True,
        excluido=False,
    )


@pytest.fixture(scope='session')
def mock_user_not_existent():
    """
    Mock user entity not existent
    """
    return UserEntity(
        email=NOT_EXISTENT_EMAIL,
        nome="Luiz Souza",
        telefone="11999999999",
        uuid=NOT_EXISTENT_UUID,
        imagem_perfil=None,
        ativo=True,
        excluido=False,
    )

@pytest_asyncio.fixture(scope='session')
async def get_jwt_tokens(mock_user_repo: MockUserRepository):
    """
    Get jwt tokens
    """
    service = LoginService(mock_user_repo)
    return await service.login("email@existent-mock", USER_PASSWORD)
