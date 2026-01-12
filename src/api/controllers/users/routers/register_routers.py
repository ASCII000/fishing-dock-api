"""
Routers for register Api Domain
"""

from fastapi import APIRouter, Depends
from ..schemas import UserRequestSchema, UserTokensResponseSchema
from ..services import RegisterController


router = APIRouter()


@router.post("")
async def create_user(
    user: UserRequestSchema,
    controller: RegisterController = Depends()
) -> UserTokensResponseSchema:
    """
    Create user
    """
    return await controller.create_new_user(user)
