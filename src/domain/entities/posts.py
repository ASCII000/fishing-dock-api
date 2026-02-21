"""
Posts entity
"""

from dataclasses import dataclass

from .topics import TopicEntity
from .blob import BlobEntity


@dataclass
class PostEntity:
    """
    Post entity
    """

    id: int
    title: str
    description: str
    image: BlobEntity
    topic: TopicEntity
