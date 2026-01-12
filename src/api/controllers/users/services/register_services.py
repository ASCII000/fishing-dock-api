"""
Register services
"""

import uuid

from fastapi import Depends

from api.dependencies.connections import get_repository
from database.repositories import UserRepository
from domain.entities import UserEntity
from domain.users import RegisterService, LoginService
from ..schemas import UserRequestSchema, UserTokensResponseSchema


class RegisterController:
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

    async def create_new_user(self, user: UserRequestSchema) -> UserTokensResponseSchema:
        """
        Method for create user
        """
        # Create user entity
        user_entity = UserEntity(
            email=user.email,
            nome=user.nome,
            telefone=user.telefone,
            uuid=str(uuid.uuid4()),
            imagem_perfil=None,
            ativo=True,
            excluido=False,
        )

        # Set user password
        user_entity.set_password(user.senha)

        # Create user
        created_user = await self.register_service.create_new_user(user_entity)

        # Generate tokens
        tokens = await self.login_service.login(
            email=created_user.email,
            password=user.senha,
        )

        return UserTokensResponseSchema(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )
