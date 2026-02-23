"""
Posts Handler
"""

from io import BytesIO
from typing import List, Optional

from fastapi import Depends, UploadFile, HTTPException, status
from PIL import Image

from api.dependencies.connections import get_repository
from database.repositories import PostRepository, BlobRepository, UserRepository, TopicRepository
from domain.services.topics.posts_service import PostService
from domain.services.blob.blob_services import BlobService
from domain.entities import PostEntity
from domain.exceptions import BlobException
from setup import storage_blob
from integrations.blob_storage import StorageProviders, BlobStorageAdapter
from ..schemas import PostUpdateSchema, PostResponseSchema, BlobResponseSchema


class PostsController:
    """
    Posts controller
    """

    def __init__(
        self,
        post_repo: PostRepository = Depends(get_repository(PostRepository)),
        blob_repo: BlobRepository = Depends(get_repository(BlobRepository)),
        user_repo: UserRepository = Depends(get_repository(UserRepository)),
        topic_repo: TopicRepository = Depends(get_repository(TopicRepository)),
    ):
        self.post_repo = post_repo
        self.blob_repo = blob_repo
        self.user_repo = user_repo
        self.topic_repo = topic_repo
        self.post_service = PostService(post_repo)

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

    def _validate_image_dimensions(self, file_content: bytes, filename: str, min_width: int = 650, min_height: int = 360) -> None:
        """
        Validate image dimensions
        """
        try:
            image = Image.open(BytesIO(file_content))
            width, height = image.size
            if width < min_width or height < min_height:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image '{filename}' dimensions must be at least {min_width}x{min_height}. Got {width}x{height}"
                )
        except HTTPException:
            raise
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image file: {filename}"
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

    async def _rollback_uploaded_blobs(self, blobs: list) -> None:
        """
        Delete uploaded blobs in case of failure (rollback)
        """
        for blob in blobs:
            try:
                await self.blob_service.delete(blob.id)
            except Exception:
                pass  # Ignore errors during rollback

    async def create_post(
        self,
        topic_id: int,
        title: str,
        description: str,
        reply_post_id: Optional[int],
        files: List[UploadFile],
        user_uuid: str
    ) -> PostResponseSchema:
        """
        Create a new post with optional file attachments
        """
        user_id = await self._get_user_id(user_uuid)

        # Upload files if provided
        uploaded_blobs = []
        try:
            for file in files:
                if file and file.filename:
                    file_content = await file.read()
                    file_name = file.filename.rsplit('.', 1)[0] if '.' in file.filename else file.filename

                    # Validate image dimensions (min 650x360)
                    self._validate_image_dimensions(file_content, file.filename)

                    # Convert to webp
                    file_content = self._convert_to_webp(file_content)

                    blob = await self.blob_service.upload(
                        file_name=file_name,
                        file_bytes=file_content,
                        file_extension="webp"
                    )
                    uploaded_blobs.append(blob)

        except HTTPException:
            # Rollback uploaded blobs on validation error
            await self._rollback_uploaded_blobs(uploaded_blobs)
            raise

        except BlobException as err:
            # Rollback uploaded blobs on upload error
            await self._rollback_uploaded_blobs(uploaded_blobs)
            raise HTTPException(
                status_code=err.code,
                detail={"message": err.message, "detail": err.detail}
            ) from err

        post_entity = PostEntity(
            id=0,
            title=title,
            description=description,
            user_id=user_id,
            reply_post_id=reply_post_id,
            likes_count=0,
            reply_count=0,
            topic_post_id=topic_id,
            post_apppends=uploaded_blobs
        )

        # Case the post is a reply, additionally post origin reply counter
        if reply_post_id:

            # Verify the post exists
            original_post = await self.post_repo.get_by_id(reply_post_id)
            if not original_post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Original post not found for reply"
                )

            # Increment reply counter
            await self.post_repo.increment_reply_count(reply_post_id, 1)

        # Increment topic post counter
        await self.topic_repo.increment_post_count(topic_id, 1)

        result = await self.post_service.create(topic_id, user_id, post_entity)

        return PostResponseSchema(
            id=result.id,
            title=result.titulo,
            description=result.descricao,
            user_id=result.usuario_id,
            reply_post_id=result.resposta_post_id,
            likes_count=result.gostei_contador,
            reply_count=result.resposta_contador,
            topic_post_id=result.topico_post_id,
            appends=[
                BlobResponseSchema(
                    id=blob.id,
                    link=blob.link,
                    nome=blob.nome,
                    extensao=blob.extensao
                ) for blob in uploaded_blobs
            ]
        )

    async def update_post(
        self,
        post_id: int,
        data: PostUpdateSchema,
        user_uuid: str
    ) -> PostResponseSchema:
        """
        Update a post
        """
        user_id = await self._get_user_id(user_uuid)
        existing_post = await self.post_repo.get_by_id(post_id)

        if existing_post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        if data.title is not None:
            existing_post.title = data.title
        if data.description is not None:
            existing_post.description = data.description

        result = await self.post_service.update(existing_post, user_id)

        return PostResponseSchema(
            id=result.id,
            title=result.titulo,
            description=result.descricao,
            user_id=result.usuario_id,
            reply_post_id=result.resposta_post_id,
            likes_count=result.gostei_contador,
            reply_count=result.resposta_contador,
            topic_post_id=result.topico_post_id,
            appends=[]
        )

    async def get_post(self, post_id: int) -> PostResponseSchema:
        """
        Get a post by ID
        """
        post = await self.post_repo.get_by_id(post_id)

        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        return PostResponseSchema(
            id=post.id,
            title=post.title,
            description=post.description,
            user_id=post.user_id,
            reply_post_id=post.reply_post_id,
            likes_count=post.likes_count,
            reply_count=post.reply_count,
            topic_post_id=post.topic_post_id,
            appends=[
                BlobResponseSchema(
                    id=blob.id,
                    link=blob.link,
                    nome=blob.nome,
                    extensao=blob.extensao
                ) for blob in post.post_apppends
            ]
        )

    async def upload_post_appends(
        self,
        post_id: int,
        files: List[UploadFile],
        user_uuid: str
    ) -> PostResponseSchema:
        """
        Upload append files for a post
        """
        user_id = await self._get_user_id(user_uuid)
        existing_post = await self.post_repo.get_by_id(post_id)

        if existing_post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        # Verify user owns the post
        if existing_post.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to modify this post"
            )

        uploaded_blobs = []
        try:
            for file in files:
                file_content = await file.read()
                file_name = file.filename.rsplit('.', 1)[0] if '.' in file.filename else file.filename

                # Validate image dimensions (min 650x360)
                self._validate_image_dimensions(file_content, file.filename)

                # Convert to webp
                file_content = self._convert_to_webp(file_content)

                blob = await self.blob_service.upload(
                    file_name=file_name,
                    file_bytes=file_content,
                    file_extension="webp"
                )
                uploaded_blobs.append(blob)

        except HTTPException:
            # Rollback uploaded blobs on validation error
            await self._rollback_uploaded_blobs(uploaded_blobs)
            raise

        except BlobException as err:
            # Rollback uploaded blobs on upload error
            await self._rollback_uploaded_blobs(uploaded_blobs)
            raise HTTPException(
                status_code=err.code,
                detail={"message": err.message, "detail": err.detail}
            ) from err

        # Save appends to posts_anexos table
        if uploaded_blobs:
            await self.post_repo.add_appends(post_id, uploaded_blobs)

        # Refresh post to get updated appends
        updated_post = await self.post_repo.get_by_id(post_id)

        return PostResponseSchema(
            id=updated_post.id,
            title=updated_post.title,
            description=updated_post.description,
            user_id=updated_post.user_id,
            reply_post_id=updated_post.reply_post_id,
            likes_count=updated_post.likes_count,
            reply_count=updated_post.reply_count,
            topic_post_id=updated_post.topic_post_id,
            appends=[
                BlobResponseSchema(
                    id=blob.id,
                    link=blob.link,
                    nome=blob.nome,
                    extensao=blob.extensao
                ) for blob in updated_post.post_apppends
            ]
        )

    async def delete_post_append(
        self,
        post_id: int,
        append_id: int,
        user_uuid: str
    ) -> PostResponseSchema:
        """
        Delete an append file from a post
        """
        user_id = await self._get_user_id(user_uuid)
        existing_post = await self.post_repo.get_by_id(post_id)

        if existing_post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        # Verify user owns the post
        if existing_post.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to modify this post"
            )

        try:

            # Delete the blob
            await self.blob_service.delete(append_id)

        except BlobException as err:

            raise HTTPException(
                status_code=err.code,
                detail={"message": err.message, "detail": err.detail}
            ) from err

        # Mark append as removed in entity
        existing_post.remove_append(append_id)

        # Refresh post
        updated_post = await self.post_repo.get_by_id(post_id)

        return PostResponseSchema(
            id=updated_post.id,
            title=updated_post.title,
            description=updated_post.description,
            user_id=updated_post.user_id,
            reply_post_id=updated_post.reply_post_id,
            likes_count=updated_post.likes_count,
            reply_count=updated_post.reply_count,
            topic_post_id=updated_post.topic_post_id,
            appends=[
                BlobResponseSchema(
                    id=blob.id,
                    link=blob.link,
                    nome=blob.nome,
                    extensao=blob.extensao
                ) for blob in updated_post.post_apppends
            ]
        )
