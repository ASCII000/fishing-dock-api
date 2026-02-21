"""
Repository for blob storage
"""

from abc import ABC, abstractmethod

from ..entities.blob import BlobEntity


class IBlobRepository(ABC):
    """
    Repository for blob storage
    """

    @abstractmethod
    async def get_file(self, file_id: str) -> BlobEntity:
        """
        Method for get file from storage

        Args:
            file_id: str

        Returns:
            BlobEntity: The file entity
        """

    @abstractmethod
    async def create(self, file: BlobEntity) -> BlobEntity:
        """
        Method for upload file to storage

        Args:
            file: BlobEntity

        Returns:
            BlobEntity: The uploaded file entity
        """
