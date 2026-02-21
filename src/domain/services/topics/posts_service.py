"""
Posts service
"""

from ...repositories import IPostRepository
from ...entities import PostEntity, UserEntity


class PostService:
    """
    Posts service
    """

    def __init__(self, post_repository: IPostRepository):
        self.post_repository = post_repository

    async def create(self, topic_id: int, post: PostEntity, user: UserEntity):
        """
        Method to create a new post
        """