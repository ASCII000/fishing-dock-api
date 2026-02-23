"""
Interfaces for blob Storages
"""

from abc import ABC, abstractmethod

from .schemas import FileSchema


class IBlobStorage(ABC):
    """
    Interface for blob Storages
    """

    @abstractmethod
    async def upload_archive(
        self,
        file_name: str,
        file_extension: str,
        file_content: bytes,
    ) -> FileSchema:
        """
        Upload archive

        Args:
            file_name (str) : File name
            file_extension (str) : File extension
            file_content (bytes) : File content
        """

    @abstractmethod
    async def delete_archive(self, file_id: str) -> None:
        """
        Delete archive

        Args:
            file_id (str) : File id
        """
