"""
Register services
"""

import uuid

from fastapi import Depends, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.concurrency import run_in_threadpool

from setup import storage_blob, StorageProviders
from utils.converters import convert_bytes_image_to_webp
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

    async def create_new_user(self, user: UserRequestSchema, avatar: UploadFile) -> UserTokensResponseSchema:
        """
        Method for create user
        """

        # Create user entity
        user_entity = UserEntity(
            email=user.email,
            nome=user.nome,
            telefone=user.telefone,
            uuid=str(uuid.uuid4()),
            avatar_url=None,
            ativo=True,
            excluido=False,
        )

        if avatar:

            # Upload user avatar
            blob_provider = storage_blob.get(StorageProviders.SUPABASE)
            supported_types = ("image/png", "image/jpeg", "image/jpg", "image/webp")

            if avatar.content_type not in supported_types:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Não aceitamos arquivo do formato {avatar.content_type.split('/')[1]}, aceitamos apenas "
                        f"os formatos {', '.join([t.replace('image/', '') for t in supported_types])}"
                    )
                )

            file_bytes = await avatar.read()
            webp_bytes = await run_in_threadpool(convert_bytes_image_to_webp, file_bytes)

            user_avatar = await blob_provider.upload_archive(
                file_content=webp_bytes,
                file_extension="webp",
                file_name=avatar.filename,
            )

            user_entity.avatar_url = user_avatar.link

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
