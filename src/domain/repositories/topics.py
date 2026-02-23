"""
Topics repository
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

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

    @abstractmethod
    async def increment_post_count(self, topic_id: int, quantity: int) -> None:
        """
        Increment post count for a topic
        """

    @abstractmethod
    async def search(
        self,
        search: Optional[str],
        page: int,
        items_per_page: int
    ) -> Tuple[List[TopicEntity], int]:
        """
        Search topics by title or id with pagination
        Returns tuple of (topics, total_count)
        """
