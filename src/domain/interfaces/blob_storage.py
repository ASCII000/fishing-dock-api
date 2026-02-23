"""
Blob storage interface for domain layer
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BlobUploadResult:
    """
    Result of uploading a blob
    """
    id: str
    name: str
    link: str
    created_at: Optional[datetime] = None


class IBlobStorageProvider(ABC):
    """
    Interface for blob storage providers.
    This abstraction allows the domain layer to not depend on specific implementations.
    """

    @abstractmethod
    async def upload(
        self,
        file_name: str,
        file_extension: str,
        file_content: bytes,
    ) -> BlobUploadResult:
        """
        Upload a file to the storage provider.

        Args:
            file_name: Name of the file
            file_extension: Extension of the file
            file_content: Content of the file as bytes

        Returns:
            BlobUploadResult with the uploaded file info
        """

    @abstractmethod
    async def delete(self, file_id: str) -> None:
        """
        Delete a file from the storage provider.

        Args:
            file_id: ID of the file to delete
        """
