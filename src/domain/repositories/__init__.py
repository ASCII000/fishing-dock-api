"""
Initialize repositories
"""

from .user import IUserRepository
from .blob import IBlobRepository


__all__ = [
    "IUserRepository",
    "IBlobRepository",
]
