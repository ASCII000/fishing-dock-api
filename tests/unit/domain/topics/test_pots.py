"""
Tests for posts service
"""

import pytest

from src.domain.entities import PostEntity
from src.domain.services.topics.posts_service import PostService
from src.domain.exceptions import BaseDomainException
from tests.unit.mock import MockPostRepository


@pytest.fixture
def mock_post_repo():
    """
    Mock post repository fixture
    """
    return MockPostRepository()


@pytest.fixture
def post_service(mock_post_repo):
    """
    Post service fixture
    """
    return PostService(mock_post_repo)


@pytest.fixture
def sample_post():
    """
    Sample post entity fixture
    """
    return PostEntity(
        id=0,
        title="Test Post",
        description="Test Post Description",
        user_id=1,
        reply_post_id=None,
        likes_count=0,
        reply_count=0,
        topic_post_id=1,
        post_apppends=[]
    )


class TestPostService:
    """
    Tests for PostService
    """

    @pytest.mark.asyncio
    async def test_create_post_success(self, post_service, sample_post):
        """
        Test creating a post successfully
        """
        result = await post_service.create(
            topic_id=1,
            user_id=1,
            post=sample_post
        )

        assert result is not None
        assert result.id == 1
        assert result.title == "Test Post"
        assert result.description == "Test Post Description"

    @pytest.mark.asyncio
    async def test_update_post_success(self, post_service, sample_post):
        """
        Test updating a post successfully
        """
        created = await post_service.create(
            topic_id=1,
            user_id=1,
            post=sample_post
        )

        created.title = "Updated Post Title"
        result = await post_service.update(created, created.user_id)

        assert result is not None
        assert result.title == "Updated Post Title"

    @pytest.mark.asyncio
    async def test_update_post_unauthorized(self, post_service, sample_post):
        """
        Test updating a post without permission
        """
        created = await post_service.create(
            topic_id=1,
            user_id=1,
            post=sample_post
        )

        with pytest.raises(BaseDomainException) as exc_info:
            await post_service.update(created, 999)

        assert "permission" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_post_by_id(self, mock_post_repo, sample_post):
        """
        Test getting a post by ID
        """
        created = await mock_post_repo.create(1, 1, sample_post)

        result = await mock_post_repo.get_by_id(created.id)

        assert result is not None
        assert result.id == created.id
        assert result.title == sample_post.title

    @pytest.mark.asyncio
    async def test_get_post_not_found(self, mock_post_repo):
        """
        Test getting a post that doesn't exist
        """
        result = await mock_post_repo.get_by_id(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_create_reply_post(self, post_service, sample_post):
        """
        Test creating a reply to a post
        """
        original = await post_service.create(
            topic_id=1,
            user_id=1,
            post=sample_post
        )

        reply_post = PostEntity(
            id=0,
            title="Reply Post",
            description="This is a reply",
            user_id=2,
            reply_post_id=original.id,
            likes_count=0,
            reply_count=0,
            topic_post_id=1,
            post_apppends=[]
        )

        result = await post_service.create(
            topic_id=1,
            user_id=2,
            post=reply_post
        )

        assert result is not None
        assert result.reply_post_id == original.id
