"""
Tests for topics handler
"""

import pytest
from io import BytesIO
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, UploadFile

from src.api.controllers.topics.handlers.topics_handler import TopicsController
from src.api.controllers.topics.schemas import TopicUpdateSchema
from src.domain.entities import TopicEntity, BlobEntity
from domain.exceptions import BlobException
from tests.unit.mock import MockTopicRepository, MockBlobRepository, MockUserRepository, MockBlobStorageProvider


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


class TestTopicsController:
    """
    Tests for TopicsController
    """

    @pytest.fixture
    def mock_topic_repo(self):
        return MockTopicRepository()

    @pytest.fixture
    def mock_blob_repo(self):
        return MockBlobRepository()

    @pytest.fixture
    def mock_user_repo(self):
        return MockUserRepository()

    @pytest.fixture
    def mock_blob_provider(self):
        return MockBlobStorageProvider()

    @pytest.fixture
    def controller(self, mock_topic_repo, mock_blob_repo, mock_user_repo, mock_blob_provider):
        """
        Create a controller with mocked dependencies
        """
        with patch('src.api.controllers.topics.handlers.topics_handler.storage_blob') as mock_storage, \
             patch('src.api.controllers.topics.handlers.topics_handler.BlobStorageAdapter') as mock_adapter:

            mock_storage.get.return_value = MagicMock()
            mock_adapter.return_value = mock_blob_provider

            controller = TopicsController.__new__(TopicsController)
            controller.topic_repo = mock_topic_repo
            controller.blob_repo = mock_blob_repo
            controller.user_repo = mock_user_repo
            controller.topic_service = MagicMock()
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
        controller._validate_image_dimensions(image_content)  # Should not raise

    def test_validate_image_dimensions_too_small(self, controller):
        """Test validating image dimensions when too small"""
        image_content = create_mock_image(400, 200)

        with pytest.raises(HTTPException) as exc_info:
            controller._validate_image_dimensions(image_content)

        assert exc_info.value.status_code == 400
        assert "650x360" in exc_info.value.detail

    def test_validate_image_dimensions_invalid_file(self, controller):
        """Test validating image dimensions with invalid file"""
        with pytest.raises(HTTPException) as exc_info:
            controller._validate_image_dimensions(b"not an image")

        assert exc_info.value.status_code == 400
        assert "Invalid image file" in exc_info.value.detail

    # Test create_topic
    @pytest.mark.asyncio
    async def test_create_topic_success(self, controller):
        """Test creating a topic successfully"""
        image_content = create_mock_image(800, 600)
        mock_file = create_upload_file(image_content, "test.png")

        mock_blob = BlobEntity(
            id=1,
            provedor="test",
            provedor_id="test-id",
            link="http://test.com/image.png",
            nome="test",
            extensao="png"
        )
        controller.blob_service.upload = AsyncMock(return_value=mock_blob)

        mock_result = MagicMock()
        mock_result.id = 1
        mock_result.titulo = "Test Topic"
        mock_result.descricao = "Test Description"
        mock_result.quantidade_posts = 0
        mock_result.topico_thumbnail_blob_id = 1
        mock_result.criado_por_id = 1
        mock_result.criado_em = datetime.now()
        controller.topic_service.create = AsyncMock(return_value=mock_result)

        result = await controller.create_topic(
            title="Test Topic",
            description="Test Description",
            image=mock_file,
            user_uuid="valid-uuid"
        )

        assert result.id == 1
        assert result.title == "Test Topic"
        controller.blob_service.upload.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_topic_no_image(self, controller):
        """Test creating a topic without image raises error"""
        with pytest.raises(HTTPException) as exc_info:
            await controller.create_topic(
                title="Test Topic",
                description="Test Description",
                image=None,
                user_uuid="valid-uuid"
            )

        assert exc_info.value.status_code == 400
        assert "required" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_create_topic_image_too_small(self, controller):
        """Test creating a topic with image too small"""
        image_content = create_mock_image(400, 200)
        mock_file = create_upload_file(image_content, "test.png")

        with pytest.raises(HTTPException) as exc_info:
            await controller.create_topic(
                title="Test Topic",
                description="Test Description",
                image=mock_file,
                user_uuid="valid-uuid"
            )

        assert exc_info.value.status_code == 400
        assert "650x360" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_topic_blob_exception(self, controller):
        """Test creating a topic when blob upload fails"""
        image_content = create_mock_image(800, 600)
        mock_file = create_upload_file(image_content, "test.png")

        controller.blob_service.upload = AsyncMock(
            side_effect=BlobException("Upload failed", 500, {"error": "test"})
        )

        with pytest.raises(HTTPException) as exc_info:
            await controller.create_topic(
                title="Test Topic",
                description="Test Description",
                image=mock_file,
                user_uuid="valid-uuid"
            )

        assert exc_info.value.status_code == 500

    # Test update_topic
    @pytest.mark.asyncio
    async def test_update_topic_success(self, controller):
        """Test updating a topic successfully"""
        existing_topic = TopicEntity(
            id=1,
            title="Old Title",
            description="Old Description",
            topic_image_id=1,
            created_by_user_id=1,
            qtd_posts=0,
            created_at=datetime.now()
        )
        controller.topic_repo.get_by_id = AsyncMock(return_value=existing_topic)

        mock_result = MagicMock()
        mock_result.id = 1
        mock_result.titulo = "New Title"
        mock_result.descricao = "New Description"
        mock_result.quantidade_posts = 0
        mock_result.topico_thumbnail_blob_id = 1
        mock_result.criado_por_id = 1
        mock_result.criado_em = datetime.now()
        controller.topic_service.update = AsyncMock(return_value=mock_result)

        update_data = TopicUpdateSchema(title="New Title", description="New Description")
        result = await controller.update_topic(1, update_data, "valid-uuid")

        assert result.title == "New Title"

    # Test get_topic
    @pytest.mark.asyncio
    async def test_get_topic_success(self, controller):
        """Test getting a topic successfully"""
        topic = TopicEntity(
            id=1,
            title="Test Topic",
            description="Test Description",
            topic_image_id=1,
            created_by_user_id=1,
            qtd_posts=5,
            created_at=datetime.now()
        )
        controller.topic_repo.get_by_id = AsyncMock(return_value=topic)

        result = await controller.get_topic(1)

        assert result.id == 1
        assert result.title == "Test Topic"
        assert result.qtd_posts == 5

    # Test upload_topic_image
    @pytest.mark.asyncio
    async def test_upload_topic_image_success(self, controller):
        """Test uploading topic image successfully"""
        image_content = create_mock_image(800, 600)
        mock_file = create_upload_file(image_content, "new_image.png")

        existing_topic = TopicEntity(
            id=1,
            title="Test Topic",
            description="Test Description",
            topic_image_id=None,
            created_by_user_id=1,
            qtd_posts=0,
            created_at=datetime.now()
        )
        controller.topic_repo.get_by_id = AsyncMock(return_value=existing_topic)

        mock_blob = BlobEntity(
            id=2,
            provedor="test",
            provedor_id="test-id",
            link="http://test.com/new_image.png",
            nome="new_image",
            extensao="png"
        )
        controller.blob_service.upload = AsyncMock(return_value=mock_blob)
        controller.blob_service.delete = AsyncMock()

        mock_result = MagicMock()
        mock_result.id = 1
        mock_result.titulo = "Test Topic"
        mock_result.descricao = "Test Description"
        mock_result.quantidade_posts = 0
        mock_result.topico_thumbnail_blob_id = 2
        mock_result.criado_por_id = 1
        mock_result.criado_em = datetime.now()
        controller.topic_service.update = AsyncMock(return_value=mock_result)

        result = await controller.upload_topic_image(1, mock_file, "valid-uuid")

        assert result.topic_image_id == 2
        controller.blob_service.upload.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_topic_image_replaces_old(self, controller):
        """Test uploading topic image replaces old image"""
        image_content = create_mock_image(800, 600)
        mock_file = create_upload_file(image_content, "new_image.png")

        existing_topic = TopicEntity(
            id=1,
            title="Test Topic",
            description="Test Description",
            topic_image_id=1,
            created_by_user_id=1,
            qtd_posts=0,
            created_at=datetime.now()
        )
        controller.topic_repo.get_by_id = AsyncMock(return_value=existing_topic)

        mock_blob = BlobEntity(
            id=2,
            provedor="test",
            provedor_id="test-id",
            link="http://test.com/new_image.png",
            nome="new_image",
            extensao="png"
        )
        controller.blob_service.upload = AsyncMock(return_value=mock_blob)
        controller.blob_service.delete = AsyncMock()

        mock_result = MagicMock()
        mock_result.id = 1
        mock_result.titulo = "Test Topic"
        mock_result.descricao = "Test Description"
        mock_result.quantidade_posts = 0
        mock_result.topico_thumbnail_blob_id = 2
        mock_result.criado_por_id = 1
        mock_result.criado_em = datetime.now()
        controller.topic_service.update = AsyncMock(return_value=mock_result)

        result = await controller.upload_topic_image(1, mock_file, "valid-uuid")

        controller.blob_service.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_upload_topic_image_blob_exception(self, controller):
        """Test uploading topic image when blob upload fails"""
        image_content = create_mock_image(800, 600)
        mock_file = create_upload_file(image_content, "new_image.png")

        existing_topic = TopicEntity(
            id=1,
            title="Test Topic",
            description="Test Description",
            topic_image_id=None,
            created_by_user_id=1,
            qtd_posts=0,
            created_at=datetime.now()
        )
        controller.topic_repo.get_by_id = AsyncMock(return_value=existing_topic)
        controller.blob_service.upload = AsyncMock(
            side_effect=BlobException("Upload failed", 500, {"error": "test"})
        )

        with pytest.raises(HTTPException) as exc_info:
            await controller.upload_topic_image(1, mock_file, "valid-uuid")

        assert exc_info.value.status_code == 500

    # Test delete_topic_image
    @pytest.mark.asyncio
    async def test_delete_topic_image_success(self, controller):
        """Test deleting topic image successfully"""
        existing_topic = TopicEntity(
            id=1,
            title="Test Topic",
            description="Test Description",
            topic_image_id=1,
            created_by_user_id=1,
            qtd_posts=0,
            created_at=datetime.now()
        )
        controller.topic_repo.get_by_id = AsyncMock(return_value=existing_topic)
        controller.blob_service.delete = AsyncMock()

        mock_result = MagicMock()
        mock_result.id = 1
        mock_result.titulo = "Test Topic"
        mock_result.descricao = "Test Description"
        mock_result.quantidade_posts = 0
        mock_result.topico_thumbnail_blob_id = None
        mock_result.criado_por_id = 1
        mock_result.criado_em = datetime.now()
        controller.topic_service.update = AsyncMock(return_value=mock_result)

        result = await controller.delete_topic_image(1, "valid-uuid")

        controller.blob_service.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_topic_image_no_image(self, controller):
        """Test deleting topic image when no image exists"""
        existing_topic = TopicEntity(
            id=1,
            title="Test Topic",
            description="Test Description",
            topic_image_id=None,
            created_by_user_id=1,
            qtd_posts=0,
            created_at=datetime.now()
        )
        controller.topic_repo.get_by_id = AsyncMock(return_value=existing_topic)

        result = await controller.delete_topic_image(1, "valid-uuid")

        assert result.id == 1

    @pytest.mark.asyncio
    async def test_delete_topic_image_blob_exception(self, controller):
        """Test deleting topic image when blob delete fails"""
        existing_topic = TopicEntity(
            id=1,
            title="Test Topic",
            description="Test Description",
            topic_image_id=1,
            created_by_user_id=1,
            qtd_posts=0,
            created_at=datetime.now()
        )
        controller.topic_repo.get_by_id = AsyncMock(return_value=existing_topic)
        controller.blob_service.delete = AsyncMock(
            side_effect=BlobException("Delete failed", 500, {"error": "test"})
        )

        with pytest.raises(HTTPException) as exc_info:
            await controller.delete_topic_image(1, "valid-uuid")

        assert exc_info.value.status_code == 500
