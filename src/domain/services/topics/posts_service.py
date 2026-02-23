"""
Posts service
"""

from ...repositories import IPostRepository
from ...entities import PostEntity
from ...exceptions import BaseDomainException


class PostService:
    """
    Posts service
    """

    def __init__(self, post_repository: IPostRepository):
        self.post_repository = post_repository

    async def create(self, topic_id: int, user_id: int, post: PostEntity) -> PostEntity:
        """
        Method to create a new post
        """
        return await self.post_repository.create(topic_id, user_id, post)

    async def update(self, updated_post: PostEntity, user_id: int) -> PostEntity:
        """
        Method to update a post
        """

        if user_id != updated_post.user_id:
            raise BaseDomainException("You don't have permission to update this post")

        return await self.post_repository.update(updated_post)
