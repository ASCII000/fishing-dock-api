"""
Topic service
"""

from ...repositories import ITopicRepository
from ...entities import TopicEntity, UserEntity
from ...exceptions import BaseDomainException


class TopicService:
    """
    Posts service
    """

    def __init__(self, topic_repository: ITopicRepository):
        self.topic_repository = topic_repository

    async def create(self, post: TopicEntity, user: UserEntity):
        """
        Method to create a new topic
        """
        return await self.topic_repository.create(post)

    async def update(self, topic: TopicEntity, user_id: int):
        """
        Method to update a topic
        """

        if user_id != topic.created_by_user_id:
            raise BaseDomainException(
                "You don't have permission to update this topic"
            )

        return await self.topic_repository.update(topic)    
