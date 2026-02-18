"""
Login Routers
"""

from fastapi import APIRouter, Depends
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials

from ..schemas import UserTokensResponseSchema
from ..handlers import LoginController


router = APIRouter()


@router.post("/login")
async def login_user(
    email: str,
    password: str,
    controller: LoginController = Depends()
) -> UserTokensResponseSchema:
    """
    Login user
    """
    return await controller.login(email, password)


@router.get("/refresh")
async def refresh_tokens(
    refresh_token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    controller: LoginController = Depends()
) -> UserTokensResponseSchema:
    """
    Refresh tokens
    """
    return await controller.refresh_tokens(refresh_token.credentials)
