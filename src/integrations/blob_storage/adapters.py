"""
Adapters for blob storage to domain interfaces
"""

from domain.interfaces import IBlobStorageProvider, BlobUploadResult
from .interfaces import IBlobStorage


class BlobStorageAdapter(IBlobStorageProvider):
    """
    Adapter that wraps IBlobStorage implementations to conform to domain interface.
    """

    def __init__(self, storage: IBlobStorage):
        """
        Args:
            storage: The concrete storage implementation
        """
        self._storage = storage

    async def upload(
        self,
        file_name: str,
        file_extension: str,
        file_content: bytes,
    ) -> BlobUploadResult:
        """
        Upload a file to the storage provider.
        """
        result = await self._storage.upload_archive(
            file_name=file_name,
            file_extension=file_extension,
            file_content=file_content,
        )

        return BlobUploadResult(
            id=result.id,
            name=result.name,
            link=result.link,
            created_at=result.created_at,
        )
