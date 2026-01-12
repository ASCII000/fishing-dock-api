"""
Register with Manage Users
"""

from utils import check_password_strong
from ...repositories import IUserRepository
from ...entities.user import UserEntity
from ...exceptions import DuplicateException, SecurityError


class RegisterService:
    """
    Service for register
    """


    def __init__(self, user_repository: IUserRepository):
        """
        Register Service
        """

        self.user_repo = user_repository

    async def create_new_user(self, user: UserEntity) -> UserEntity:
        """
        Method for create user

        Args:
            user: UserEntity

        Returns:
            UserEntity

        Raises:
            DuplicateException: Exception for duplicate object existence
        """

        # Verify if user already exists by email
        if await self.user_repo.get_by_email(user.email):
            raise DuplicateException(
                message="Email já em uso."
            )

        return await self.user_repo.create(user)

    async def update_user_password(self, user: UserEntity, password: str) -> UserEntity:
        """
        Update user password
        """

        # Check new password strong
        if not check_password_strong(password):
            raise SecurityError(
                "Senha fraca, ela precisa de pelo menos "
                "uma letra maiúscula, uma letra minuscula, "
                "um número e um caractere especial."
            )

        # Set new password
        user.set_password(password)
        return await self.user_repo.update_user(user)
