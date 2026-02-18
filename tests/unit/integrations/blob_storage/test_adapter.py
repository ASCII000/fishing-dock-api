"""
Tests for BlobStorageAdapter
"""

import pytest

from src.integrations.blob_storage import BlobStorageAdapter
from src.domain.interfaces.blob_storage import BlobUploadResult
from ...mock import MockBlobStorage


@pytest.fixture
def mock_storage():
    """
    Create a mock storage instance
    """
    return MockBlobStorage()


@pytest.fixture
def adapter(mock_storage):
    """
    Create an adapter with mock storage
    """
    return BlobStorageAdapter(mock_storage)


@pytest.mark.asyncio
async def test_upload_returns_blob_upload_result(adapter, mock_storage):
    """
    Test that upload returns a BlobUploadResult
    """
    result = await adapter.upload(
        file_name="test_file",
        file_extension="png",
        file_content=b"fake image content",
    )

    # Check it has the expected attributes (BlobUploadResult)
    assert hasattr(result, 'id')
    assert hasattr(result, 'name')
    assert hasattr(result, 'link')
    assert hasattr(result, 'created_at')
    assert result.id == "mock-id-1"
    assert result.name == "test_file.png"
    assert "mock-storage.example.com" in result.link
    assert result.created_at is not None


@pytest.mark.asyncio
async def test_upload_stores_file_in_mock(adapter, mock_storage):
    """
    Test that upload stores the file content
    """
    content = b"test content"
    await adapter.upload(
        file_name="my_file",
        file_extension="txt",
        file_content=content,
    )

    assert "my_file.txt" in mock_storage.uploaded_files
    assert mock_storage.uploaded_files["my_file.txt"] == content


@pytest.mark.asyncio
async def test_upload_increments_count(adapter, mock_storage):
    """
    Test that each upload increments the counter
    """
    await adapter.upload("file1", "png", b"content1")
    await adapter.upload("file2", "jpg", b"content2")
    await adapter.upload("file3", "webp", b"content3")

    assert mock_storage.upload_count == 3


@pytest.mark.asyncio
async def test_upload_generates_unique_ids(adapter):
    """
    Test that each upload gets a unique ID
    """
    result1 = await adapter.upload("file1", "png", b"content1")
    result2 = await adapter.upload("file2", "png", b"content2")

    assert result1.id != result2.id
