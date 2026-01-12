"""
Login service
"""

from fastapi import Depends, status
from fastapi.exceptions import HTTPException

import jwt

from setup import jwt_handler
from api.dependencies.connections import get_repository
from database.repositories import UserRepository
from domain.users import RegisterService, LoginService
from domain.exceptions import SecurityError
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
        self.register_service = RegisterService(user_repo)
        self.login_service = LoginService(user_repo)

    async def login(self, email: str, password: str) -> UserTokensResponseSchema:
        """
        Method for login user
        """

        try:

            # Get user tokens
            tokens = await self.login_service.login(email, password)

        except SecurityError as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=err.message,
            ) from err

        return UserTokensResponseSchema(
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
        )

    async def refresh_tokens(self, refresh_token: str) -> UserTokensResponseSchema:
        """
        Method for refresh tokens
        """

        try:

            # Refresh token
            jwt_handler.decode_payload(refresh_token)

        except (jwt.InvalidTokenError, jwt.ExpiredSignatureError) as err:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            ) from err

        try:

            tokens = await self.login_service.refresh_token(refresh_token)

        except SecurityError as err:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=err.message,
            ) from err


        return UserTokensResponseSchema(
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
        )
