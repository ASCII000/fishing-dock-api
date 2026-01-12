"""
Login and JWT controll Users
"""

from typing import TypedDict

from setup import jwt_handler, config
from ...exceptions import SecurityError
from ...repositories import IUserRepository


class UserToken(TypedDict):
    """
    Token for JWT
    """
    access_token: str
    refresh_token: str


class UserPayload(TypedDict):
    """
    Payload for JWT
    """
    nome: str
    email: str
    sub: str


class LoginService:
    """
    Login Service
    """

    def __init__(self, user_repository: IUserRepository):
        self.repo = user_repository

    async def login(self, email: str, password: str) -> UserToken:
        """
        Login user

        Args:
            email: str
            password: str

        Returns:
            UserToken: Access and refresh token
        
        Raises:
            SecurityError: Exception for security error
        """

        user = await self.repo.get_by_email(email)
        if not user or not user.authenticated(password):
            raise SecurityError("Email ou senha incorretos.")

        access_token = {
            "tipo": "ACCESS",
            "nome": user.nome,
            "email": user.email,
            "sub": user.uuid,
        }

        acces_token = jwt_handler.encode_payload(
            access_token,
            config.JWT_ACCESS_TOKEN_EXPIRES
        )

        refresh_token = {
            "tipo": "REFRESH",
            "sub": user.uuid,
        }

        refresh_token = jwt_handler.encode_payload(
            refresh_token,
            config.JWT_REFRESH_TOKEN_EXPIRES
        )

        return UserToken(
            access_token=acces_token,
            refresh_token=refresh_token
        )

    async def refresh_token(self, refresh_token: str) -> UserToken:
        """
        Refresh token

        Args:
            refresh_token: str

        Returns:
            UserToken: Access and refresh token
        """

        payload = jwt_handler.decode_payload(refresh_token)
        if payload["tipo"] != "REFRESH":
            raise SecurityError("Token inválido.")

        user = await self.repo.get_by_uuid(payload["sub"])

        access_token = {
            "tipo": "ACCESS",
            "nome": user.nome,
            "email": user.email,
            "sub": user.uuid,
        }

        access_token = jwt_handler.encode_payload(
            access_token,
            config.JWT_ACCESS_TOKEN_EXPIRES
        )

        refresh_token = {
            "tipo": "REFRESH",
            "sub": user.uuid,
        }

        refresh_token = jwt_handler.encode_payload(
            refresh_token,
            config.JWT_REFRESH_TOKEN_EXPIRES
        )

        return UserToken(
            access_token=access_token,
            refresh_token=refresh_token
        )
