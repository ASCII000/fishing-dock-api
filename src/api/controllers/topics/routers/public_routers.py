"""
Public Topics Routers - No authentication required
"""

import math
from typing import Optional

from fastapi import APIRouter, Depends, Query, Path

from api.dependencies.connections import get_repository
from database.repositories import TopicRepository, PostRepository
from ..schemas import (
    TopicPaginatedResponseSchema,
    TopicPublicResponseSchema,
    PostPaginatedResponseSchema,
    PostPublicResponseSchema,
    BlobResponseSchema,
    PaginationMeta,
)


router = APIRouter(prefix="/public", tags=["public"])


@router.get(
    "/topics",
    response_model=TopicPaginatedResponseSchema,
    summary="Search topics",
    description="Search topics by title or ID with pagination. No authentication required."
)
async def search_topics(
    search: Optional[str] = Query(None, description="Search by topic title or ID"),
    page: int = Query(1, ge=1, description="Page number"),
    items_per_page: int = Query(10, ge=1, le=50, description="Items per page (max 50)"),
    topic_repo: TopicRepository = Depends(get_repository(TopicRepository))
) -> TopicPaginatedResponseSchema:
    """
    Search topics with pagination
    """
    topics, total_count = await topic_repo.search(search, page, items_per_page)

    total_pages = math.ceil(total_count / items_per_page) if total_count > 0 else 0

    return TopicPaginatedResponseSchema(
        data=[
            TopicPublicResponseSchema(
                id=topic.id,
                title=topic.title,
                description=topic.description,
                qtd_posts=topic.qtd_posts,
                topic_image_id=topic.topic_image_id,
                created_at=topic.created_at
            ) for topic in topics
        ],
        pagination=PaginationMeta(
            page=page,
            items_per_page=items_per_page,
            total_items=total_count,
            total_pages=total_pages
        )
    )


@router.get(
    "/topics/{topic_id}/posts",
    response_model=PostPaginatedResponseSchema,
    summary="Search posts in a topic",
    description="Search posts by title or ID within a topic with pagination. No authentication required."
)
async def search_posts(
    topic_id: int = Path(..., description="Topic ID"),
    search: Optional[str] = Query(None, description="Search by post title or ID"),
    page: int = Query(1, ge=1, description="Page number"),
    items_per_page: int = Query(10, ge=1, le=50, description="Items per page (max 50)"),
    post_repo: PostRepository = Depends(get_repository(PostRepository))
) -> PostPaginatedResponseSchema:
    """
    Search posts in a topic with pagination
    """
    posts, total_count = await post_repo.search(topic_id, search, page, items_per_page)

    total_pages = math.ceil(total_count / items_per_page) if total_count > 0 else 0

    return PostPaginatedResponseSchema(
        data=[
            PostPublicResponseSchema(
                id=post.id,
                title=post.title,
                description=post.description,
                reply_post_id=post.reply_post_id,
                likes_count=post.likes_count,
                reply_count=post.reply_count,
                topic_post_id=post.topic_post_id,
                appends=[
                    BlobResponseSchema(
                        id=blob.id,
                        link=blob.link,
                        nome=blob.nome,
                        extensao=blob.extensao
                    ) for blob in post.post_apppends
                ]
            ) for post in posts
        ],
        pagination=PaginationMeta(
            page=page,
            items_per_page=items_per_page,
            total_items=total_count,
            total_pages=total_pages
        )
    )
