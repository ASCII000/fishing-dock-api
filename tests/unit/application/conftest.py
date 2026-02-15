# pylint: disable=redefined-outer-name

"""
Configuration for application tests
"""

import pytest
import pytest_asyncio

import sqlmodel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport

from src.api.app import app


DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope='function')
async def async_client():
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

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Drop tables after test
    async with engine.begin() as conn:
        await conn.run_sync(sqlmodel.SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope='module')
def valid_user_data():
    """
    Valid user data for testing
    """
    return {
        "nome": "Test User",
        "email": "test@example.com",
        "telefone": "11999999999",
        "senha": "StrongPass123!"
    }


@pytest.fixture(scope='module')
def invalid_user_data():
    """
    Invalid user data for testing
    """
    return {
        "nome": "Test User",
        "email": "invalid-email",
        "telefone": "11999999999",
        "senha": "weak"
    }
