"""
Topics Routers
"""

from .topics_routers import router as topics_router
from .posts_routers import router as posts_router
from .public_routers import router as public_router


__all__ = [
    "topics_router",
    "posts_router",
    "public_router",
]
