"""
Mock users reference
"""

from src.domain.repositories.user import IUserRepository
from src.domain.entities.user import UserEntity


USER_PASSWORD = "password"

NOT_EXISTENT_UUID = "uuid-existent-mock"
NOT_EXISTENT_EMAIL = "email@not-existent-mock"


class MockUserRepository(IUserRepository):
    """
    Mock user repository
    """

    async def create(self, user: UserEntity) -> UserEntity:
        """
        Create user
        """
        return user

    async def get_by_uuid(self, uuid: str) -> UserEntity:
        """
        Get user by uuid
        """
        if uuid == NOT_EXISTENT_UUID:
            return None

        user = UserEntity(
            email="email",
            nome="name",
            telefone="phone",
            uuid=uuid,
            imagem_perfil=None,
            ativo=True,
            excluido=False,
        )

        user.set_password(USER_PASSWORD)
        return user

    async def get_by_email(self, email: str) -> UserEntity:
        """
        Get user by email
        """
        if email == NOT_EXISTENT_EMAIL:
            return None

        user = UserEntity(
            email=email,
            nome="name",
            telefone="phone",
            uuid="uuid",
            imagem_perfil=None,
            ativo=True,
            excluido=False,
        )

        user.set_password(USER_PASSWORD)
        return user

    async def update_user(self, user: UserEntity) -> UserEntity:
        """
        Update user
        """
        return user
