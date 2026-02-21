"""
Topics service
"""

from ...entities import TopicEntity, PostEntity, UserEntity


class TopicService:
    """
    Topic service
    """

    def __init__(self, topic_repository, post_repository):
        self.topic_repository = topic_repository
        self.post_repository = post_repository

    def create(self, topic: TopicEntity, user: UserEntity):
        """
        Method to create a new topic
        """

    def create_new_post(self, topic: TopicEntity, post: PostEntity, user: UserEntity):
        """
        Method to create a new post
        """