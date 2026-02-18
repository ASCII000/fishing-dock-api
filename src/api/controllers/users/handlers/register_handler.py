"""
Register handler
"""

import uuid

from fastapi import Depends, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.concurrency import run_in_threadpool

from setup import storage_blob, StorageProviders
from utils.converters import convert_bytes_image_to_webp
from api.dependencies.connections import get_repository
from database.repositories import UserRepository, BlobRepository
from domain.entities import UserEntity
from domain.services.users import RegisterService, LoginService
from domain.services.blob import BlobService
from integrations.blob_storage import BlobStorageAdapter
from ..schemas import UserRequestSchema, UserTokensResponseSchema


class RegisterController:
    """
    User registration handler
    """

    def __init__(
        self,
        user_repo: UserRepository = Depends(get_repository(UserRepository)),
        blob_repo: BlobRepository = Depends(get_repository(BlobRepository)),
    ):
        self.user_repo = user_repo
        self.blob_repo = blob_repo
        self.register_service = RegisterService(user_repo)
        self.login_service = LoginService(user_repo)

        # Create blob service with storage adapter
        storage = storage_blob.get(StorageProviders.SUPABASE)
        storage_adapter = BlobStorageAdapter(storage)
        self.blob_service = BlobService(
            blob_repository=blob_repo,
            storage_provider=storage_adapter,
            provider_name=StorageProviders.SUPABASE.value,
        )

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
            avatar_blob_id=None,
            ativo=True,
            excluido=False,
        )

        if avatar:

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

            user_avatar = await self.blob_service.upload(
                file_name=f"{user_entity.uuid}_avatar",
                file_bytes=webp_bytes,
                file_extension="webp",
            )

            user_entity.avatar_blob_id = user_avatar.id

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
