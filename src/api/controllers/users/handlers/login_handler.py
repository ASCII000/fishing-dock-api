"""
Login service
"""

from fastapi import Depends

from setup import jwt_handler
from api.dependencies.connections import get_repository
from database.repositories import UserRepository
from domain.services.users import LoginService
from ..schemas import UserTokensResponseSchema


class LoginController:
    """
    User service
    """

    def __init__(
        self,
        user_repo: UserRepository = Depends(get_repository(UserRepository))
    ):
        self.user_repo = user_repo
        self.login_service = LoginService(user_repo)

    async def login(self, email: str, password: str) -> UserTokensResponseSchema:
        """
        Method for login user
        """
        tokens = await self.login_service.login(email, password)

        return UserTokensResponseSchema(
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
        )

    async def refresh_tokens(self, refresh_token: str) -> UserTokensResponseSchema:
        """
        Method for refresh tokens
        """
        # Valida token antes de renovar
        jwt_handler.decode_payload(refresh_token)

        tokens = await self.login_service.refresh_token(refresh_token)

        return UserTokensResponseSchema(
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
        )
