"""
Topics repository
"""

from abc import ABC, abstractmethod

from ..entities import TopicEntity


class ITopicRepository(ABC):
    """
    Topics repository
    """

    @abstractmethod
    async def create(self, topic: TopicEntity) -> TopicEntity:
        """
        Create a new topic
        """

    @abstractmethod
    async def update(self, topic: TopicEntity) -> TopicEntity:
        """
        Update a topic
        """

    @abstractmethod
    async def get_by_id(self, topic_id: int) -> TopicEntity:
        """
        Get topic by id
        """
