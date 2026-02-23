"""
Topics Schemas
"""

from datetime import datetime
from typing import Optional, List, Generic, TypeVar

from pydantic import BaseModel, Field


class TopicCreateSchema(BaseModel):
    """
    Schema for creating a new topic (used for documentation only, actual data via Form)
    """
    title: str = Field(..., description="Topic title", min_length=1, max_length=255)
    description: str = Field(..., description="Topic description")


class TopicUpdateSchema(BaseModel):
    """
    Schema for updating a topic
    """
    title: Optional[str] = Field(None, description="Topic title", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Topic description")
    topic_image_id: Optional[int] = Field(None, description="Topic image blob ID")


class TopicResponseSchema(BaseModel):
    """
    Schema for topic response
    """
    model_config = {"from_attributes": True}

    id: int = Field(..., description="Topic ID")
    title: str = Field(..., description="Topic title")
    description: str = Field(..., description="Topic description")
    qtd_posts: int = Field(..., description="Number of posts")
    topic_image_id: Optional[int] = Field(None, description="Topic image blob ID")
    created_by_user_id: int = Field(..., description="User ID who created the topic")
    created_at: datetime = Field(..., description="Creation date")


class TopicPublicResponseSchema(BaseModel):
    """
    Schema for public topic response (without sensitive data)
    """
    model_config = {"from_attributes": True}

    id: int = Field(..., description="Topic ID")
    title: str = Field(..., description="Topic title")
    description: str = Field(..., description="Topic description")
    qtd_posts: int = Field(..., description="Number of posts")
    topic_image_id: Optional[int] = Field(None, description="Topic image blob ID")
    created_at: datetime = Field(..., description="Creation date")


class PaginationMeta(BaseModel):
    """
    Pagination metadata
    """
    page: int = Field(..., description="Current page")
    items_per_page: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total items")
    total_pages: int = Field(..., description="Total pages")


class TopicPaginatedResponseSchema(BaseModel):
    """
    Paginated topics response
    """
    data: List[TopicPublicResponseSchema] = Field(..., description="List of topics")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
