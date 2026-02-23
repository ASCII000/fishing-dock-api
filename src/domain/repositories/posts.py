"""
Topics repository
"""

from abc import ABC, abstractmethod

from ..entities import PostEntity


class IPostRepository(ABC):
    """
    Topics repository
    """

    @abstractmethod
    async def create(self, topic: PostEntity) -> PostEntity:
        """
        Create a new topic
        """

    @abstractmethod
    async def update(self, topic: PostEntity) -> PostEntity:
        """
        Update a topic
        """

    @abstractmethod
    async def get_by_id(self, topic_id: int) -> PostEntity:
        """
        Get topic by id
        """
