"""
Tests for MockBlobStorage implementation
"""

import pytest

from src.integrations.blob_storage.schemas import FileSchema
from ...mock import MockBlobStorage


@pytest.fixture
def mock_storage():
    """
    Create a fresh mock storage instance
    """
    return MockBlobStorage()


@pytest.mark.asyncio
async def test_upload_archive_returns_file_schema(mock_storage):
    """
    Test that upload_archive returns a FileSchema
    """
    result = await mock_storage.upload_archive(
        file_name="test_image",
        file_extension="webp",
        file_content=b"fake image bytes",
    )

    assert isinstance(result, FileSchema)
    assert result.id == "mock-id-1"
    assert result.name == "test_image.webp"
    assert "test_image.webp" in result.link
    assert result.created_at is not None


@pytest.mark.asyncio
async def test_upload_archive_stores_content(mock_storage):
    """
    Test that upload_archive stores the file content
    """
    content = b"binary content here"
    await mock_storage.upload_archive(
        file_name="document",
        file_extension="pdf",
        file_content=content,
    )

    assert "document.pdf" in mock_storage.uploaded_files
    assert mock_storage.uploaded_files["document.pdf"] == content


@pytest.mark.asyncio
async def test_multiple_uploads_tracked(mock_storage):
    """
    Test that multiple uploads are tracked correctly
    """
    await mock_storage.upload_archive("file1", "png", b"content1")
    await mock_storage.upload_archive("file2", "jpg", b"content2")

    assert mock_storage.upload_count == 2
    assert len(mock_storage.uploaded_files) == 2
    assert "file1.png" in mock_storage.uploaded_files
    assert "file2.jpg" in mock_storage.uploaded_files
