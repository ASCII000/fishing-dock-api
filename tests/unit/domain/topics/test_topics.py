"""
Tests for topics service
"""

import pytest
from datetime import datetime

from src.domain.entities import TopicEntity
from src.domain.services.topics.topics_service import TopicService
from src.domain.exceptions import BaseDomainException
from tests.unit.mock import MockTopicRepository


@pytest.fixture
def mock_topic_repo():
    """
    Mock topic repository fixture
    """
    return MockTopicRepository()


@pytest.fixture
def topic_service(mock_topic_repo):
    """
    Topic service fixture
    """
    return TopicService(mock_topic_repo)


@pytest.fixture
def sample_topic():
    """
    Sample topic entity fixture
    """
    return TopicEntity(
        id=0,
        title="Test Topic",
        description="Test Description",
        topic_image_id=1,
        created_by_user_id=1,
        qtd_posts=0,
        created_at=datetime.now()
    )


class TestTopicService:
    """
    Tests for TopicService
    """

    @pytest.mark.asyncio
    async def test_create_topic_success(self, topic_service, sample_topic):
        """
        Test creating a topic successfully
        """
        result = await topic_service.create(sample_topic, None)

        assert result is not None
        assert result.id == 1
        assert result.title == "Test Topic"
        assert result.description == "Test Description"

    @pytest.mark.asyncio
    async def test_update_topic_success(self, topic_service, sample_topic, mock_topic_repo):
        """
        Test updating a topic successfully
        """
        created = await topic_service.create(sample_topic, None)

        created.title = "Updated Title"
        result = await topic_service.update(created, created.created_by_user_id)

        assert result is not None
        assert result.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_update_topic_unauthorized(self, topic_service, sample_topic):
        """
        Test updating a topic without permission
        """
        created = await topic_service.create(sample_topic, None)

        with pytest.raises(BaseDomainException) as exc_info:
            await topic_service.update(created, 999)

        assert "permission" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_topic_by_id(self, mock_topic_repo, sample_topic):
        """
        Test getting a topic by ID
        """
        created = await mock_topic_repo.create(sample_topic)

        result = await mock_topic_repo.get_by_id(created.id)

        assert result is not None
        assert result.id == created.id
        assert result.title == sample_topic.title

    @pytest.mark.asyncio
    async def test_get_topic_not_found(self, mock_topic_repo):
        """
        Test getting a topic that doesn't exist
        """
        result = await mock_topic_repo.get_by_id(999)

        assert result is None
