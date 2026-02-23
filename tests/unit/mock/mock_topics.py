"""
Mock topics and posts repositories
"""

from datetime import datetime
from typing import Dict, Optional, List

from src.domain.repositories.topics import ITopicRepository
from src.domain.repositories.posts import IPostRepository
from src.domain.repositories.blob import IBlobRepository
from src.domain.entities import TopicEntity, PostEntity, BlobEntity


class MockTopicRepository(ITopicRepository):
    """
    Mock topic repository
    """

    def __init__(self):
        self._topics: Dict[int, TopicEntity] = {}
        self._counter = 1

    async def create(self, topic: TopicEntity) -> TopicEntity:
        """
        Create a new topic
        """
        topic.id = self._counter
        self._topics[topic.id] = topic
        self._counter += 1
        return topic

    async def update(self, topic: TopicEntity) -> TopicEntity:
        """
        Update a topic
        """
        if topic.id in self._topics:
            self._topics[topic.id] = topic
        return topic

    async def get_by_id(self, topic_id: int) -> TopicEntity:
        """
        Get topic by id
        """
        return self._topics.get(topic_id)

    async def increment_post_count(self, topic_id: int, quantity: int) -> None:
        """
        Increment post count for a topic
        """
        if topic_id in self._topics:
            self._topics[topic_id].qtd_posts += quantity

    async def search(
        self,
        search: Optional[str],
        page: int,
        items_per_page: int
    ) -> tuple:
        """
        Search topics by title or id with pagination
        """
        topics = list(self._topics.values())

        # Apply search filter
        if search:
            if search.isdigit():
                topics = [
                    t for t in topics
                    if t.id == int(search) or search.lower() in t.title.lower()
                ]
            else:
                topics = [
                    t for t in topics
                    if search.lower() in t.title.lower()
                ]

        total_count = len(topics)

        # Apply pagination
        offset = (page - 1) * items_per_page
        topics = topics[offset:offset + items_per_page]

        return topics, total_count


class MockPostRepository(IPostRepository):
    """
    Mock post repository
    """

    def __init__(self):
        self._posts: Dict[int, PostEntity] = {}
        self._counter = 1

    async def create(self, topic_id: int, user_id: int, post: PostEntity) -> PostEntity:
        """
        Create a new post
        """
        post.id = self._counter
        post.topic_post_id = topic_id
        post.user_id = user_id
        self._posts[post.id] = post
        self._counter += 1
        return post

    async def update(self, post: PostEntity) -> PostEntity:
        """
        Update a post
        """
        if post.id in self._posts:
            self._posts[post.id] = post
        return post

    async def get_by_id(self, post_id: int) -> PostEntity:
        """
        Get post by id
        """
        return self._posts.get(post_id)

    async def increment_reply_count(self, post_id: int, quantity: int) -> None:
        """
        Increment reply count for a post
        """
        if post_id in self._posts:
            self._posts[post_id].reply_count += quantity

    async def add_appends(self, post_id: int, blobs: List[BlobEntity]) -> None:
        """
        Add appends to a post
        """
        if post_id in self._posts:
            post = self._posts[post_id]
            if post.post_apppends is None:
                post.post_apppends = []
            post.post_apppends.extend(blobs)

    async def search(
        self,
        topic_id: int,
        search: Optional[str],
        page: int,
        items_per_page: int
    ) -> tuple:
        """
        Search posts by title or id with pagination
        """
        # Filter by topic_id
        posts = [p for p in self._posts.values() if p.topic_post_id == topic_id]

        # Apply search filter
        if search:
            if search.isdigit():
                posts = [
                    p for p in posts
                    if p.id == int(search) or search.lower() in p.title.lower()
                ]
            else:
                posts = [
                    p for p in posts
                    if search.lower() in p.title.lower()
                ]

        total_count = len(posts)

        # Apply pagination
        offset = (page - 1) * items_per_page
        posts = posts[offset:offset + items_per_page]

        return posts, total_count


class MockBlobRepository(IBlobRepository):
    """
    Mock blob repository
    """

    def __init__(self):
        self._blobs: Dict[int, BlobEntity] = {}
        self._counter = 1

    async def create(self, file: BlobEntity) -> BlobEntity:
        """
        Create a new blob
        """
        file.id = self._counter
        self._blobs[file.id] = file
        self._counter += 1
        return file

    async def get_file(self, file_id: int) -> Optional[BlobEntity]:
        """
        Get blob by id
        """
        return self._blobs.get(file_id)

    async def delete(self, file_id: int) -> None:
        """
        Delete blob by id
        """
        if file_id in self._blobs:
            del self._blobs[file_id]
