"""
Setup topics controllers
"""

from fastapi import FastAPI

from .routers.topics_routers import router as topics_router
from .routers.posts_routers import router as posts_router
from .routers.public_routers import router as public_router


def setup_topics_controllers(app: FastAPI):
    """
    Setup topics controllers

    Args:
        app: FastAPI
    """

    app.include_router(topics_router, prefix="/topics", tags=["Topics"])
    app.include_router(posts_router, prefix="/topics", tags=["Posts"])
    app.include_router(public_router)
