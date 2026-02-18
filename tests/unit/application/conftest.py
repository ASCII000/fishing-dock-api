# pylint: disable=redefined-outer-name

"""
Configuration for application tests
"""

import io
from unittest.mock import patch

import pytest
import pytest_asyncio

import sqlmodel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport

from src.api.app import app
from src.integrations.blob_storage import BlobStorageFactory, StorageProviders
from ..mock import MockBlobStorage


DATABASE_URL = "sqlite+aiosqlite:///:memory:"


def create_test_image():
    """
    Create a minimal valid PNG image for testing
    """
    # Minimal 1x1 transparent PNG
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
        b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
        b'\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return io.BytesIO(png_data)


@pytest.fixture(scope='function')
def mock_blob_storage_factory():
    """
    Create a mock blob storage factory
    """
    factory = BlobStorageFactory()
    factory.register(StorageProviders.SUPABASE, MockBlobStorage())
    return factory


@pytest_asyncio.fixture(scope='function')
async def async_client(mock_blob_storage_factory):
    """
    Create async client for testing
    """
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True
    )

    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(sqlmodel.SQLModel.metadata.create_all)

    # Set session on app state
    app.state.async_session = async_session

    # Patch the storage_blob with our mock
    with patch('src.setup.storage_blob', mock_blob_storage_factory):
        with patch('src.api.controllers.users.handlers.register_handler.storage_blob', mock_blob_storage_factory):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                yield client

    # Drop tables after test
    async with engine.begin() as conn:
        await conn.run_sync(sqlmodel.SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope='function')
def valid_user_data():
    """
    Valid user data for testing (form data)
    """
    return {
        "username": "Test User",
        "email": "test@example.com",
        "phone": "11999999999",
        "password": "StrongPass123!"
    }


@pytest.fixture(scope='function')
def valid_user_files():
    """
    Valid user files for testing (avatar)
    """
    return {
        "avatar": ("test_avatar.png", create_test_image(), "image/png")
    }


@pytest.fixture(scope='module')
def invalid_user_data():
    """
    Invalid user data for testing
    """
    return {
        "username": "Test User",
        "email": "invalid-email",
        "phone": "11999999999",
        "password": "weak"
    }
