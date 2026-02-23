"""
Posts repository
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from ..entities import PostEntity, BlobEntity


class IPostRepository(ABC):
    """
    Posts repository
    """

    @abstractmethod
    async def create(self, topic_id: int, user_id: int, post: PostEntity) -> PostEntity:
        """
        Create a new post
        """

    @abstractmethod
    async def update(self, topic: PostEntity) -> PostEntity:
        """
        Update a topic
        """

    @abstractmethod
    async def get_by_id(self, post_id: int) -> PostEntity:
        """
        Get topic by id
        """

    @abstractmethod
    async def increment_reply_count(self, post_id: int, quantity: int) -> None:
        """
        Increment reply count for a post
        """

    @abstractmethod
    async def add_appends(self, post_id: int, blobs: List[BlobEntity]) -> None:
        """
        Add appends to a post
        """

    @abstractmethod
    async def search(
        self,
        topic_id: int,
        search: Optional[str],
        page: int,
        items_per_page: int
    ) -> Tuple[List[PostEntity], int]:
        """
        Search posts by title or id with pagination
        Returns tuple of (posts, total_count)
        """
