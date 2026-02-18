"""
Tests for BlobStorageFactory
"""

import pytest

from src.integrations.blob_storage import (
    BlobStorageFactory,
    StorageProviders,
    BlobStorageException,
)
from ...mock import MockBlobStorage


def test_register_and_get_provider():
    """
    Test registering and retrieving a storage provider
    """
    factory = BlobStorageFactory()
    mock_storage = MockBlobStorage()

    factory.register(StorageProviders.SUPABASE, mock_storage)
    retrieved = factory.get(StorageProviders.SUPABASE)

    assert retrieved is mock_storage


def test_get_unregistered_provider_raises_exception():
    """
    Test that getting an unregistered provider raises BlobStorageException
    """
    factory = BlobStorageFactory()

    with pytest.raises(BlobStorageException) as exc_info:
        factory.get(StorageProviders.SUPABASE)

    assert exc_info.value.code == 404
    assert "not found" in exc_info.value.message.lower()


def test_register_multiple_providers():
    """
    Test registering multiple providers
    """
    factory = BlobStorageFactory()
    mock_storage = MockBlobStorage()

    factory.register(StorageProviders.SUPABASE, mock_storage)

    # Should be able to retrieve
    assert factory.get(StorageProviders.SUPABASE) is mock_storage


def test_override_registered_provider():
    """
    Test that registering a provider twice overrides the first
    """
    factory = BlobStorageFactory()
    mock_storage1 = MockBlobStorage()
    mock_storage2 = MockBlobStorage()

    factory.register(StorageProviders.SUPABASE, mock_storage1)
    factory.register(StorageProviders.SUPABASE, mock_storage2)

    assert factory.get(StorageProviders.SUPABASE) is mock_storage2
