"""
Blob service
"""

from ...entities.blob import BlobEntity
from ...exceptions import BlobException
from ...interfaces import IBlobStorageProvider
from ...repositories.blob import IBlobRepository


class BlobService:
    """
    File service
    """

    def __init__(
        self,
        blob_repository: IBlobRepository,
        storage_provider: IBlobStorageProvider,
        provider_name: str,
    ):
        """
        Initialize the file service with the blob repository and storage provider
        """
        self.blob_repository = blob_repository
        self.storage_provider = storage_provider
        self.provider_name = provider_name

    async def upload(
        self,
        file_name: str,
        file_bytes: bytes,
        file_extension: str,
    ) -> BlobEntity:
        """
        Upload file to storage and return the file URL
        """

        try:
            # Upload the file to storage (Cloud)
            uploaded_file = await self.storage_provider.upload(
                file_name=file_name,
                file_content=file_bytes,
                file_extension=file_extension,
            )

        except Exception as err:
            # Preserve error details if available
            code = getattr(err, 'code', 500)
            detail = getattr(err, 'detail', str(err))
            message = getattr(err, 'message', "Error uploading file to storage")
            raise BlobException(message, code, detail) from err

        # Save file information to database
        blob_entity = BlobEntity(
            provedor=self.provider_name,
            provedor_id=uploaded_file.id,
            link=uploaded_file.link,
            nome=file_name,
            extensao=file_extension,
        )

        blob_model = await self.blob_repository.create(blob_entity)
        return blob_model

    async def delete(self, blob_id: int) -> None:
        """
        Delete file from storage and database
        """
        # Get file info from database
        blob = await self.blob_repository.get_file(blob_id)

        if not blob:
            return

        try:
            # Delete from cloud storage
            await self.storage_provider.delete(blob.provedor_id)

        except Exception as err:
            # Preserve error details if available
            code = getattr(err, 'code', 500)
            detail = getattr(err, 'detail', str(err))
            message = getattr(err, 'message', "Error deleting file from storage")
            raise BlobException(message, code, detail) from err

        # Delete from database
        await self.blob_repository.delete(blob_id)
