"""
Tests for blob service
"""

import pytest

from src.domain.services.blob.blob_services import BlobService
from src.domain.entities import BlobEntity
from tests.unit.mock import MockBlobRepository, MockBlobStorageProvider


@pytest.fixture
def mock_blob_repo():
    """
    Mock blob repository fixture
    """
    return MockBlobRepository()


@pytest.fixture
def mock_storage_provider():
    """
    Mock storage provider fixture
    """
    return MockBlobStorageProvider()


@pytest.fixture
def blob_service(mock_blob_repo, mock_storage_provider):
    """
    Blob service fixture
    """
    return BlobService(mock_blob_repo, mock_storage_provider, "mock-provider")


class TestBlobService:
    """
    Tests for BlobService
    """

    @pytest.mark.asyncio
    async def test_upload_file_success(self, blob_service, mock_storage_provider):
        """
        Test uploading a file successfully
        """
        result = await blob_service.upload(
            file_name="test_file",
            file_bytes=b"test content",
            file_extension="txt"
        )

        assert result is not None
        assert result.id == 1
        assert result.nome == "test_file"
        assert result.extensao == "txt"
        assert mock_storage_provider.upload_count == 1

    @pytest.mark.asyncio
    async def test_upload_multiple_files(self, blob_service, mock_storage_provider):
        """
        Test uploading multiple files
        """
        await blob_service.upload("file1", b"content1", "txt")
        await blob_service.upload("file2", b"content2", "jpg")
        await blob_service.upload("file3", b"content3", "pdf")

        assert mock_storage_provider.upload_count == 3
        assert len(mock_storage_provider.uploaded_files) == 3

    @pytest.mark.asyncio
    async def test_delete_file_success(self, blob_service, mock_blob_repo, mock_storage_provider):
        """
        Test deleting a file successfully
        """
        # First upload a file
        uploaded = await blob_service.upload("test_file", b"content", "txt")

        # Verify file exists
        file_before = await mock_blob_repo.get_file(uploaded.id)
        assert file_before is not None

        # Delete the file
        await blob_service.delete(uploaded.id)

        # Verify file was deleted from repository
        file_after = await mock_blob_repo.get_file(uploaded.id)
        assert file_after is None

        # Verify delete was called on storage provider
        assert len(mock_storage_provider.deleted_files) == 1

    @pytest.mark.asyncio
    async def test_delete_nonexistent_file(self, blob_service, mock_storage_provider):
        """
        Test deleting a file that doesn't exist (should not raise error)
        """
        await blob_service.delete(999)

        # Should not call delete on storage provider if file doesn't exist
        assert len(mock_storage_provider.deleted_files) == 0

    @pytest.mark.asyncio
    async def test_upload_returns_blob_entity(self, blob_service):
        """
        Test that upload returns a BlobEntity with correct data
        """
        result = await blob_service.upload("myfile", b"data", "png")

        assert isinstance(result, BlobEntity)
        assert result.provedor == "mock-provider"
        assert result.nome == "myfile"
        assert result.extensao == "png"
        assert result.link is not None
