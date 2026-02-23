"""
Tests for posts handler
"""

import pytest
from io import BytesIO
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, UploadFile

from src.api.controllers.topics.handlers.posts_handler import PostsController
from src.api.controllers.topics.schemas import PostUpdateSchema
from src.domain.entities import PostEntity, BlobEntity
from domain.exceptions import BlobException
from tests.unit.mock import MockPostRepository, MockBlobRepository, MockUserRepository, MockBlobStorageProvider, MockTopicRepository


def create_mock_image(width: int = 800, height: int = 600) -> bytes:
    """
    Create a mock image with given dimensions
    """
    from PIL import Image
    img = Image.new('RGB', (width, height), color='red')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def create_upload_file(content: bytes, filename: str = "test.png") -> UploadFile:
    """
    Create an UploadFile mock
    """
    file = MagicMock(spec=UploadFile)
    file.filename = filename
    file.read = AsyncMock(return_value=content)
    return file


class TestPostsController:
    """
    Tests for PostsController
    """

    @pytest.fixture
    def mock_post_repo(self):
        return MockPostRepository()

    @pytest.fixture
    def mock_blob_repo(self):
        return MockBlobRepository()

    @pytest.fixture
    def mock_user_repo(self):
        return MockUserRepository()

    @pytest.fixture
    def mock_topic_repo(self):
        return MockTopicRepository()

    @pytest.fixture
    def mock_blob_provider(self):
        return MockBlobStorageProvider()

    @pytest.fixture
    def controller(self, mock_post_repo, mock_blob_repo, mock_user_repo, mock_topic_repo, mock_blob_provider):
        """
        Create a controller with mocked dependencies
        """
        with patch('src.api.controllers.topics.handlers.posts_handler.storage_blob') as mock_storage, \
             patch('src.api.controllers.topics.handlers.posts_handler.BlobStorageAdapter') as mock_adapter:

            mock_storage.get.return_value = MagicMock()
            mock_adapter.return_value = mock_blob_provider

            controller = PostsController.__new__(PostsController)
            controller.post_repo = mock_post_repo
            controller.blob_repo = mock_blob_repo
            controller.user_repo = mock_user_repo
            controller.topic_repo = mock_topic_repo
            controller.post_service = MagicMock()
            controller.blob_service = MagicMock()

            return controller

    # Test _get_user_id
    @pytest.mark.asyncio
    async def test_get_user_id_success(self, controller):
        """Test getting user ID from UUID successfully"""
        result = await controller._get_user_id("valid-uuid")
        assert result == 1

    @pytest.mark.asyncio
    async def test_get_user_id_not_found(self, controller):
        """Test getting user ID when user not found"""
        from tests.unit.mock.mock_users import NOT_EXISTENT_UUID

        with pytest.raises(HTTPException) as exc_info:
            await controller._get_user_id(NOT_EXISTENT_UUID)

        assert exc_info.value.status_code == 404
        assert "User not found" in exc_info.value.detail

    # Test _validate_image_dimensions
    def test_validate_image_dimensions_success(self, controller):
        """Test validating image dimensions successfully"""
        image_content = create_mock_image(800, 600)
        controller._validate_image_dimensions(image_content, "test.png")  # Should not raise

    def test_validate_image_dimensions_too_small(self, controller):
        """Test validating image dimensions when too small"""
        image_content = create_mock_image(400, 200)

        with pytest.raises(HTTPException) as exc_info:
            controller._validate_image_dimensions(image_content, "test.png")

        assert exc_info.value.status_code == 400
        assert "650x360" in exc_info.value.detail

    def test_validate_image_dimensions_invalid_file(self, controller):
        """Test validating image dimensions with invalid file"""
        with pytest.raises(HTTPException) as exc_info:
            controller._validate_image_dimensions(b"not an image", "test.png")

        assert exc_info.value.status_code == 400
        assert "Invalid image file" in exc_info.value.detail

    # Test create_post
    @pytest.mark.asyncio
    async def test_create_post_success_without_files(self, controller):
        """Test creating a post without files successfully"""
        mock_result = MagicMock()
        mock_result.id = 1
        mock_result.titulo = "Test Post"
        mock_result.descricao = "Test Description"
        mock_result.usuario_id = 1
        mock_result.resposta_post_id = None
        mock_result.gostei_contador = 0
        mock_result.resposta_contador = 0
        mock_result.topico_post_id = 1
        controller.post_service.create = AsyncMock(return_value=mock_result)

        result = await controller.create_post(
            topic_id=1,
            title="Test Post",
            description="Test Description",
            reply_post_id=None,
            files=[],
            user_uuid="valid-uuid"
        )

        assert result.id == 1
        assert result.title == "Test Post"

    @pytest.mark.asyncio
    async def test_create_post_success_with_files(self, controller):
        """Test creating a post with files successfully"""
        image_content = create_mock_image(800, 600)
        mock_file = create_upload_file(image_content, "attachment.png")

        mock_blob = BlobEntity(
            id=1,
            provedor="test",
            provedor_id="test-id",
            link="http://test.com/attachment.png",
            nome="attachment",
            extensao="png"
        )
        controller.blob_service.upload = AsyncMock(return_value=mock_blob)

        mock_result = MagicMock()
        mock_result.id = 1
        mock_result.titulo = "Test Post"
        mock_result.descricao = "Test Description"
        mock_result.usuario_id = 1
        mock_result.resposta_post_id = None
        mock_result.gostei_contador = 0
        mock_result.resposta_contador = 0
        mock_result.topico_post_id = 1
        controller.post_service.create = AsyncMock(return_value=mock_result)

        result = await controller.create_post(
            topic_id=1,
            title="Test Post",
            description="Test Description",
            reply_post_id=None,
            files=[mock_file],
            user_uuid="valid-uuid"
        )

        assert result.id == 1
        controller.blob_service.upload.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_post_file_too_small(self, controller):
        """Test creating a post with file too small"""
        image_content = create_mock_image(400, 200)
        mock_file = create_upload_file(image_content, "attachment.png")

        with pytest.raises(HTTPException) as exc_info:
            await controller.create_post(
                topic_id=1,
                title="Test Post",
                description="Test Description",
                reply_post_id=None,
                files=[mock_file],
                user_uuid="valid-uuid"
            )

        assert exc_info.value.status_code == 400
        assert "650x360" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_post_blob_exception(self, controller):
        """Test creating a post when blob upload fails"""
        image_content = create_mock_image(800, 600)
        mock_file = create_upload_file(image_content, "attachment.png")

        controller.blob_service.upload = AsyncMock(
            side_effect=BlobException("Upload failed", 500, {"error": "test"})
        )

        with pytest.raises(HTTPException) as exc_info:
            await controller.create_post(
                topic_id=1,
                title="Test Post",
                description="Test Description",
                reply_post_id=None,
                files=[mock_file],
                user_uuid="valid-uuid"
            )

        assert exc_info.value.status_code == 500

    # Test update_post
    @pytest.mark.asyncio
    async def test_update_post_success(self, controller):
        """Test updating a post successfully"""
        existing_post = PostEntity(
            id=1,
            title="Old Title",
            description="Old Description",
            user_id=1,
            reply_post_id=None,
            likes_count=0,
            reply_count=0,
            topic_post_id=1,
            post_apppends=[]
        )
        controller.post_repo.get_by_id = AsyncMock(return_value=existing_post)

        mock_result = MagicMock()
        mock_result.id = 1
        mock_result.titulo = "New Title"
        mock_result.descricao = "New Description"
        mock_result.usuario_id = 1
        mock_result.resposta_post_id = None
        mock_result.gostei_contador = 0
        mock_result.resposta_contador = 0
        mock_result.topico_post_id = 1
        controller.post_service.update = AsyncMock(return_value=mock_result)

        update_data = PostUpdateSchema(title="New Title", description="New Description")
        result = await controller.update_post(1, update_data, "valid-uuid")

        assert result.title == "New Title"

    # Test get_post
    @pytest.mark.asyncio
    async def test_get_post_success(self, controller):
        """Test getting a post successfully"""
        post = PostEntity(
            id=1,
            title="Test Post",
            description="Test Description",
            user_id=1,
            reply_post_id=None,
            likes_count=5,
            reply_count=3,
            topic_post_id=1,
            post_apppends=[]
        )
        controller.post_repo.get_by_id = AsyncMock(return_value=post)

        result = await controller.get_post(1)

        assert result.id == 1
        assert result.title == "Test Post"
        assert result.likes_count == 5

    # Test upload_post_appends
    @pytest.mark.asyncio
    async def test_upload_post_appends_success(self, controller):
        """Test uploading post appends successfully"""
        image_content = create_mock_image(800, 600)
        mock_file = create_upload_file(image_content, "new_attachment.png")

        existing_post = PostEntity(
            id=1,
            title="Test Post",
            description="Test Description",
            user_id=1,
            reply_post_id=None,
            likes_count=0,
            reply_count=0,
            topic_post_id=1,
            post_apppends=[]
        )
        controller.post_repo.get_by_id = AsyncMock(return_value=existing_post)

        mock_blob = BlobEntity(
            id=2,
            provedor="test",
            provedor_id="test-id",
            link="http://test.com/new_attachment.png",
            nome="new_attachment",
            extensao="png"
        )
        controller.blob_service.upload = AsyncMock(return_value=mock_blob)

        result = await controller.upload_post_appends(1, [mock_file], "valid-uuid")

        controller.blob_service.upload.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_post_appends_unauthorized(self, controller):
        """Test uploading post appends without permission"""
        image_content = create_mock_image(800, 600)
        mock_file = create_upload_file(image_content, "new_attachment.png")

        existing_post = PostEntity(
            id=1,
            title="Test Post",
            description="Test Description",
            user_id=999,  # Different user
            reply_post_id=None,
            likes_count=0,
            reply_count=0,
            topic_post_id=1,
            post_apppends=[]
        )
        controller.post_repo.get_by_id = AsyncMock(return_value=existing_post)

        with pytest.raises(HTTPException) as exc_info:
            await controller.upload_post_appends(1, [mock_file], "valid-uuid")

        assert exc_info.value.status_code == 403
        assert "permission" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_upload_post_appends_blob_exception(self, controller):
        """Test uploading post appends when blob upload fails"""
        image_content = create_mock_image(800, 600)
        mock_file = create_upload_file(image_content, "new_attachment.png")

        existing_post = PostEntity(
            id=1,
            title="Test Post",
            description="Test Description",
            user_id=1,
            reply_post_id=None,
            likes_count=0,
            reply_count=0,
            topic_post_id=1,
            post_apppends=[]
        )
        controller.post_repo.get_by_id = AsyncMock(return_value=existing_post)

        controller.blob_service.upload = AsyncMock(
            side_effect=BlobException("Upload failed", 500, {"error": "test"})
        )

        with pytest.raises(HTTPException) as exc_info:
            await controller.upload_post_appends(1, [mock_file], "valid-uuid")

        assert exc_info.value.status_code == 500

    # Test delete_post_append
    @pytest.mark.asyncio
    async def test_delete_post_append_success(self, controller):
        """Test deleting post append successfully"""
        mock_blob = BlobEntity(
            id=1,
            provedor="test",
            provedor_id="test-id",
            link="http://test.com/attachment.png",
            nome="attachment",
            extensao="png"
        )

        existing_post = PostEntity(
            id=1,
            title="Test Post",
            description="Test Description",
            user_id=1,
            reply_post_id=None,
            likes_count=0,
            reply_count=0,
            topic_post_id=1,
            post_apppends=[mock_blob]
        )
        controller.post_repo.get_by_id = AsyncMock(return_value=existing_post)
        controller.blob_service.delete = AsyncMock()

        result = await controller.delete_post_append(1, 1, "valid-uuid")

        controller.blob_service.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_post_append_unauthorized(self, controller):
        """Test deleting post append without permission"""
        existing_post = PostEntity(
            id=1,
            title="Test Post",
            description="Test Description",
            user_id=999,  # Different user
            reply_post_id=None,
            likes_count=0,
            reply_count=0,
            topic_post_id=1,
            post_apppends=[]
        )
        controller.post_repo.get_by_id = AsyncMock(return_value=existing_post)

        with pytest.raises(HTTPException) as exc_info:
            await controller.delete_post_append(1, 1, "valid-uuid")

        assert exc_info.value.status_code == 403
        assert "permission" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_delete_post_append_blob_exception(self, controller):
        """Test deleting post append when blob delete fails"""
        existing_post = PostEntity(
            id=1,
            title="Test Post",
            description="Test Description",
            user_id=1,
            reply_post_id=None,
            likes_count=0,
            reply_count=0,
            topic_post_id=1,
            post_apppends=[]
        )
        controller.post_repo.get_by_id = AsyncMock(return_value=existing_post)
        controller.blob_service.delete = AsyncMock(
            side_effect=BlobException("Delete failed", 500, {"error": "test"})
        )

        with pytest.raises(HTTPException) as exc_info:
            await controller.delete_post_append(1, 1, "valid-uuid")

        assert exc_info.value.status_code == 500
