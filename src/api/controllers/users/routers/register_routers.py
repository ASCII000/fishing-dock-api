"""
Routers for register Api Domain
"""

from fastapi import APIRouter, Depends
from ..schemas import UserRequestSchema, UserTokensResponseSchema
from ..services import UserController


router = APIRouter()


@router.post("")
async def create_user(
    user: UserRequestSchema,
    controller: UserController = Depends()
) -> UserTokensResponseSchema:
    """
    Create user
    """
    return await controller.create_new_user(user)
