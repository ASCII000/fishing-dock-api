"""
Topics entity
"""

from dataclasses import dataclass

from .blob import BlobEntity


@dataclass
class TopicEntity:
    """
    Topic entity
    """

    id: int
    name: str
    qtd_posts: int
    description: str
    image: BlobEntity
