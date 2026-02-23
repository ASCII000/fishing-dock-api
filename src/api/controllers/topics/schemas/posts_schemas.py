"""
Posts Schemas
"""

from typing import Optional, List

from pydantic import BaseModel, Field

from .topics_schemas import PaginationMeta


class PostCreateSchema(BaseModel):
    """
    Schema for creating a new post (used for documentation only, actual data via Form)
    """
    title: str = Field(..., description="Post title", min_length=1, max_length=255)
    description: str = Field(..., description="Post description")
    reply_post_id: Optional[int] = Field(None, description="Reply to post ID")


class PostUpdateSchema(BaseModel):
    """
    Schema for updating a post
    """
    title: Optional[str] = Field(None, description="Post title", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Post description")


class BlobResponseSchema(BaseModel):
    """
    Schema for blob response
    """
    model_config = {"from_attributes": True}

    id: int = Field(..., description="Blob ID")
    link: str = Field(..., description="Blob link")
    nome: str = Field(..., description="Blob name")
    extensao: str = Field(..., description="Blob extension")


class PostResponseSchema(BaseModel):
    """
    Schema for post response
    """
    model_config = {"from_attributes": True}

    id: int = Field(..., description="Post ID")
    title: str = Field(..., description="Post title")
    description: str = Field(..., description="Post description")
    user_id: int = Field(..., description="User ID who created the post")
    reply_post_id: Optional[int] = Field(None, description="Reply to post ID")
    likes_count: int = Field(..., description="Number of likes")
    reply_count: int = Field(..., description="Number of replies")
    topic_post_id: int = Field(..., description="Topic ID")
    appends: List[BlobResponseSchema] = Field(default_factory=list, description="List of appends")


class PostPublicResponseSchema(BaseModel):
    """
    Schema for public post response
    """
    model_config = {"from_attributes": True}

    id: int = Field(..., description="Post ID")
    title: str = Field(..., description="Post title")
    description: str = Field(..., description="Post description")
    reply_post_id: Optional[int] = Field(None, description="Reply to post ID")
    likes_count: int = Field(..., description="Number of likes")
    reply_count: int = Field(..., description="Number of replies")
    topic_post_id: int = Field(..., description="Topic ID")
    appends: List[BlobResponseSchema] = Field(default_factory=list, description="List of appends")


class PostPaginatedResponseSchema(BaseModel):
    """
    Paginated posts response
    """
    data: List[PostPublicResponseSchema] = Field(..., description="List of posts")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
