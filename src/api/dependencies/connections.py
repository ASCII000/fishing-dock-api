"""
Dependencies connections
"""

from typing import TypeVar, AsyncGenerator

from fastapi import Depends, Request

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker


T = TypeVar("T")


async def get_transaction_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Get transaction session
    """

    async_session: 'sessionmaker[AsyncSession]' = request.app.state.async_session
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

def get_repository(repositorie: T) -> T:
    """
    Get repositorie by wrapper
    """
    async def wrapper(session: AsyncSession = Depends(get_transaction_session)):
        return repositorie(session)

    return wrapper
