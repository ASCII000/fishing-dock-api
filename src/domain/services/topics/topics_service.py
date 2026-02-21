"""
Topic service
"""

from ...repositories import ITopicRepository
from ...entities import TopicEntity, UserEntity


class TopicService:
    """
    Posts service
    """

    def __init__(self, post_repository: ITopicRepository):
        self.post_repository = post_repository

    async def create(self, post: TopicEntity, user: UserEntity):
        """
        Method to create a new topic
        """