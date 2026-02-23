"""
Posts Routers
"""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form

from api.dependencies import get_current_user_uuid
from ..schemas import PostUpdateSchema, PostResponseSchema
from ..handlers import PostsController


router = APIRouter()


@router.post("/{topic_id}/posts", response_model=PostResponseSchema)
async def create_post(
    topic_id: int,
    title: str = Form(..., description="Post title", min_length=1, max_length=255),
    description: str = Form(..., description="Post description"),
    reply_post_id: Optional[int] = Form(None, description="Reply to post ID"),
    files: List[UploadFile] = File(default=[], description="Post attachments (optional)"),
    user_uuid: Annotated[str, Depends(get_current_user_uuid)] = None,
    controller: PostsController = Depends()
) -> PostResponseSchema:
    """
    Create a new post in a topic with optional file attachments
    """
    return await controller.create_post(topic_id, title, description, reply_post_id, files, user_uuid)


@router.put("/posts/{post_id}", response_model=PostResponseSchema)
async def update_post(
    post_id: int,
    data: PostUpdateSchema,
    user_uuid: Annotated[str, Depends(get_current_user_uuid)],
    controller: PostsController = Depends()
) -> PostResponseSchema:
    """
    Update a post
    """
    return await controller.update_post(post_id, data, user_uuid)


@router.get("/posts/{post_id}", response_model=PostResponseSchema)
async def get_post(
    post_id: int,
    controller: PostsController = Depends()
) -> PostResponseSchema:
    """
    Get a post by ID
    """
    return await controller.get_post(post_id)


@router.post("/posts/{post_id}/appends", response_model=PostResponseSchema)
async def upload_post_appends(
    post_id: int,
    files: List[UploadFile] = File(...),
    user_uuid: Annotated[str, Depends(get_current_user_uuid)] = None,
    controller: PostsController = Depends()
) -> PostResponseSchema:
    """
    Upload append files for a post
    """
    return await controller.upload_post_appends(post_id, files, user_uuid)


@router.delete("/posts/{post_id}/appends/{append_id}", response_model=PostResponseSchema)
async def delete_post_append(
    post_id: int,
    append_id: int,
    user_uuid: Annotated[str, Depends(get_current_user_uuid)],
    controller: PostsController = Depends()
) -> PostResponseSchema:
    """
    Delete an append file from a post
    """
    return await controller.delete_post_append(post_id, append_id, user_uuid)
