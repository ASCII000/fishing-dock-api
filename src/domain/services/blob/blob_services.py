"""
Blob service
"""

from ...entities.blob import BlobEntity
from ...exceptions import BaseDomainException
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
            raise BaseDomainException(
                "Error uploading file to storage"
            ) from err

        # Save file information to database
        blob_entity = BlobEntity(
            provedor=self.provider_name,
            provedor_id=uploaded_file.id,
            link=uploaded_file.link,
            nome=file_name,
            extensao=file_extension,
        )

        blob_model = await self.blob_repository.save(blob_entity)
        return blob_model
