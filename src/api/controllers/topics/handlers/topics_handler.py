"""
Topics Handler
"""

from datetime import datetime
from io import BytesIO

from fastapi import Depends, UploadFile, HTTPException, status
from PIL import Image

from api.dependencies.connections import get_repository
from database.repositories import TopicRepository, BlobRepository, UserRepository
from domain.services.topics.topics_service import TopicService
from domain.services.blob.blob_services import BlobService
from domain.entities import TopicEntity
from domain.exceptions import BlobException
from setup import storage_blob
from integrations.blob_storage import StorageProviders, BlobStorageAdapter
from ..schemas import TopicUpdateSchema, TopicResponseSchema


class TopicsController:
    """
    Topics controller
    """

    def __init__(
        self,
        topic_repo: TopicRepository = Depends(get_repository(TopicRepository)),
        blob_repo: BlobRepository = Depends(get_repository(BlobRepository)),
        user_repo: UserRepository = Depends(get_repository(UserRepository))
    ):
        self.topic_repo = topic_repo
        self.blob_repo = blob_repo
        self.user_repo = user_repo
        self.topic_service = TopicService(topic_repo)

        # Setup blob service
        storage = storage_blob.get(StorageProviders.SUPABASE)
        adapter = BlobStorageAdapter(storage)
        self.blob_service = BlobService(blob_repo, adapter, StorageProviders.SUPABASE.value)

    async def _get_user_id(self, user_uuid: str) -> int:
        """
        Get user ID from UUID
        """
        user = await self.user_repo.get_by_uuid(user_uuid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user.id

    def _validate_image_dimensions(self, file_content: bytes, min_width: int = 650, min_height: int = 360) -> None:
        """
        Validate image dimensions
        """
        try:
            image = Image.open(BytesIO(file_content))
            width, height = image.size
            if width < min_width or height < min_height:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image dimensions must be at least {min_width}x{min_height}. Got {width}x{height}"
                )
        except HTTPException:
            raise

        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            ) from err

    def _convert_to_webp(self, file_content: bytes) -> bytes:
        """
        Convert image to webp format
        """
        image = Image.open(BytesIO(file_content))
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGBA')
        else:
            image = image.convert('RGB')
        output = BytesIO()
        image.save(output, format='WEBP', quality=85)
        return output.getvalue()

    async def create_topic(
        self,
        title: str,
        description: str,
        image: UploadFile,
        user_uuid: str
    ) -> TopicResponseSchema:
        """
        Create a new topic with required image upload
        """
        user_id = await self._get_user_id(user_uuid)

        # Validate image is provided
        if not image or not image.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Topic image is required"
            )

        # Upload image
        file_content = await image.read()
        file_name = image.filename.rsplit('.', 1)[0] if '.' in image.filename else image.filename

        # Validate image dimensions (min 650x360)
        self._validate_image_dimensions(file_content)

        # Convert to webp
        file_content = self._convert_to_webp(file_content)

        try:
            blob = await self.blob_service.upload(
                file_name=file_name,
                file_bytes=file_content,
                file_extension="webp"
            )
            topic_image_id = blob.id
        except BlobException as err:

            raise HTTPException(
                status_code=err.code,
                detail={"message": err.message, "detail": err.detail}
            ) from err

        topic_entity = TopicEntity(
            id=0,
            title=title,
            description=description,
            topic_image_id=topic_image_id,
            created_by_user_id=user_id,
            qtd_posts=0,
            created_at=datetime.now()
        )

        result = await self.topic_service.create(topic_entity, None)

        return TopicResponseSchema(
            id=result.id,
            title=result.titulo,
            description=result.descricao,
            qtd_posts=result.quantidade_posts,
            topic_image_id=result.topico_thumbnail_blob_id,
            created_by_user_id=result.criado_por_id,
            created_at=result.criado_em
        )

    async def update_topic(
        self,
        topic_id: int,
        data: TopicUpdateSchema,
        user_uuid: str
    ) -> TopicResponseSchema:
        """
        Update a topic
        """
        user_id = await self._get_user_id(user_uuid)
        existing_topic = await self.topic_repo.get_by_id(topic_id)

        if existing_topic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )

        if data.title is not None:
            existing_topic.title = data.title
        if data.description is not None:
            existing_topic.description = data.description
        if data.topic_image_id is not None:
            existing_topic.topic_image_id = data.topic_image_id

        result = await self.topic_service.update(existing_topic, user_id)

        return TopicResponseSchema(
            id=result.id,
            title=result.titulo,
            description=result.descricao,
            qtd_posts=result.quantidade_posts,
            topic_image_id=result.topico_thumbnail_blob_id,
            created_by_user_id=result.criado_por_id,
            created_at=result.criado_em
        )

    async def get_topic(self, topic_id: int) -> TopicResponseSchema:
        """
        Get a topic by ID
        """
        topic = await self.topic_repo.get_by_id(topic_id)

        if topic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )

        return TopicResponseSchema(
            id=topic.id,
            title=topic.title,
            description=topic.description,
            qtd_posts=topic.qtd_posts,
            topic_image_id=topic.topic_image_id,
            created_by_user_id=topic.created_by_user_id,
            created_at=topic.created_at
        )

    async def upload_topic_image(
        self,
        topic_id: int,
        file: UploadFile,
        user_uuid: str
    ) -> TopicResponseSchema:
        """
        Upload image for a topic
        """
        user_id = await self._get_user_id(user_uuid)
        existing_topic = await self.topic_repo.get_by_id(topic_id)

        if existing_topic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )

        # Upload new image
        file_content = await file.read()
        file_name = file.filename.rsplit('.', 1)[0] if '.' in file.filename else file.filename

        # Validate image dimensions (min 650x360)
        self._validate_image_dimensions(file_content)

        # Convert to webp
        file_content = self._convert_to_webp(file_content)

        try:
            # Delete old image if exists
            if existing_topic.topic_image_id and existing_topic.topic_image_id > 0:
                await self.blob_service.delete(existing_topic.topic_image_id)

            blob = await self.blob_service.upload(
                file_name=file_name,
                file_bytes=file_content,
                file_extension="webp"
            )

        except BlobException as err:

            raise HTTPException(
                status_code=err.code,
                detail={"message": err.message, "detail": err.detail}
            ) from err

        # Update topic with new image
        existing_topic.topic_image_id = blob.id
        result = await self.topic_service.update(existing_topic, user_id)

        return TopicResponseSchema(
            id=result.id,
            title=result.titulo,
            description=result.descricao,
            qtd_posts=result.quantidade_posts,
            topic_image_id=result.topico_thumbnail_blob_id,
            created_by_user_id=result.criado_por_id,
            created_at=result.criado_em
        )

    async def delete_topic_image(
        self,
        topic_id: int,
        user_uuid: str
    ) -> TopicResponseSchema:
        """
        Delete image from a topic
        """
        user_id = await self._get_user_id(user_uuid)
        existing_topic = await self.topic_repo.get_by_id(topic_id)

        if existing_topic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )

        if existing_topic.topic_image_id and existing_topic.topic_image_id > 0:

            try:
                await self.blob_service.delete(existing_topic.topic_image_id)

            except BlobException as err:

                raise HTTPException(
                    status_code=err.code,
                    detail={"message": err.message, "detail": err.detail}
                ) from err

            existing_topic.topic_image_id = None
            result = await self.topic_service.update(existing_topic, user_id)
        else:
            result = existing_topic

        return TopicResponseSchema(
            id=result.id if hasattr(result, 'id') else existing_topic.id,
            title=result.titulo if hasattr(result, 'titulo') else existing_topic.title,
            description=result.descricao if hasattr(result, 'descricao') else existing_topic.description,
            qtd_posts=result.quantidade_posts if hasattr(result, 'quantidade_posts') else existing_topic.qtd_posts,
            topic_image_id=result.topico_thumbnail_blob_id if hasattr(result, 'topico_thumbnail_blob_id') else existing_topic.topic_image_id,
            created_by_user_id=result.criado_por_id if hasattr(result, 'criado_por_id') else existing_topic.created_by_user_id,
            created_at=result.criado_em if hasattr(result, 'criado_em') else existing_topic.created_at
        )
