"""
Routers for register Api Domain
"""

from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File, Form
from ..schemas import UserRequestSchema, UserTokensResponseSchema
from ..handlers import RegisterController


router = APIRouter()


@router.post("")
async def create_user(
    username: Annotated[str, Form(..., description="Username user")],
    email: Annotated[str, Form(..., description="Email user")],
    password: Annotated[str, Form(..., description="Password user")],
    phone: Annotated[str, Form(..., description="Phone user")],
    avatar: UploadFile = File(..., description="Avatar user"),
    controller: RegisterController = Depends()
) -> UserTokensResponseSchema:
    """
    Create user
    """

    data_schema = UserRequestSchema(
        nome=username,
        email=email,
        telefone=phone,
        senha=password
    )

    return await controller.create_new_user(data_schema, avatar)
