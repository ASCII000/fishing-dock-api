"""
Mock blob storage for testing
"""

from datetime import datetime
from typing import Optional

from src.domain.interfaces import IBlobStorageProvider, BlobUploadResult
from src.integrations.blob_storage import IBlobStorage
from src.integrations.blob_storage.schemas import FileSchema


class MockBlobStorage(IBlobStorage):
    """
    Mock implementation of IBlobStorage for testing
    """

    def __init__(self):
        self.uploaded_files: dict[str, bytes] = {}
        self.deleted_files: list[str] = []
        self.upload_count = 0

    async def upload_archive(
        self,
        file_name: str,
        file_extension: str,
        file_content: bytes,
    ) -> FileSchema:
        """
        Mock upload archive
        """
        self.upload_count += 1
        full_name = f"{file_name}.{file_extension}"
        self.uploaded_files[full_name] = file_content

        return FileSchema(
            id=f"mock-id-{self.upload_count}",
            name=full_name,
            link=f"https://mock-storage.example.com/{full_name}",
            created_at=datetime.now(),
        )

    async def delete_archive(self, file_id: str) -> None:
        """
        Mock delete archive
        """
        self.deleted_files.append(file_id)


class MockBlobStorageProvider(IBlobStorageProvider):
    """
    Mock implementation of IBlobStorageProvider for domain layer testing
    """

    def __init__(self):
        self.uploaded_files: dict[str, bytes] = {}
        self.deleted_files: list[str] = []
        self.upload_count = 0

    async def upload(
        self,
        file_name: str,
        file_extension: str,
        file_content: bytes,
    ) -> BlobUploadResult:
        """
        Mock upload
        """
        self.upload_count += 1
        full_name = f"{file_name}.{file_extension}"
        self.uploaded_files[full_name] = file_content

        return BlobUploadResult(
            id=f"mock-id-{self.upload_count}",
            name=full_name,
            link=f"https://mock-storage.example.com/{full_name}",
            created_at=datetime.now(),
        )

    async def delete(self, file_id: str) -> None:
        """
        Mock delete
        """
        self.deleted_files.append(file_id)
