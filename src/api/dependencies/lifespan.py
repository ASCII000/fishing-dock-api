"""
Lifespan dependencies
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

import sqlmodel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from setup import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan dependencies
    """

    # Create database session
    engine = create_async_engine(config.DATABASE_SQLITE_PATH)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    app.state.async_session = async_session

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(sqlmodel.SQLModel.metadata.create_all)

    yield

    await engine.dispose()
