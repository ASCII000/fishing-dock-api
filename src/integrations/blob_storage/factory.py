from enum import Enum

from .interfaces import IBlobStorage
from .exceptions import BlobStorageException


class StorageProviders(str, Enum):
    SUPABASE = "supabase"


class BlobStorageFactory:
    """
    Blob storage factory
    """

    def __init__(self):
        self._stores = {}

    def register(self, provider: StorageProviders, storage: IBlobStorage):
        """
        Register storage
        """

        self._stores[provider] = storage

    def get(self, provider: StorageProviders) -> IBlobStorage:
        """
        Storage provider
        """

        storage = self._stores.get(provider)

        if not storage:
            raise BlobStorageException(
                message="Provider not found",
                detail=provider.value,
                code=404,
            )

        return storage
