"""
Topics Routers
"""

from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File, Form

from api.dependencies import get_current_user_uuid
from ..schemas import TopicUpdateSchema, TopicResponseSchema
from ..handlers import TopicsController


router = APIRouter()


@router.post("", response_model=TopicResponseSchema)
async def create_topic(
    title: str = Form(..., description="Topic title", min_length=1, max_length=255),
    description: str = Form(..., description="Topic description"),
    image: UploadFile = File(..., description="Topic image (required, min 650x360)"),
    user_uuid: Annotated[str, Depends(get_current_user_uuid)] = None,
    controller: TopicsController = Depends()
) -> TopicResponseSchema:
    """
    Create a new topic with required image upload (min 650x360)
    """
    return await controller.create_topic(title, description, image, user_uuid)


@router.put("/{topic_id}", response_model=TopicResponseSchema)
async def update_topic(
    topic_id: int,
    data: TopicUpdateSchema,
    user_uuid: Annotated[str, Depends(get_current_user_uuid)],
    controller: TopicsController = Depends()
) -> TopicResponseSchema:
    """
    Update a topic
    """
    return await controller.update_topic(topic_id, data, user_uuid)


@router.get("/{topic_id}", response_model=TopicResponseSchema)
async def get_topic(
    topic_id: int,
    controller: TopicsController = Depends()
) -> TopicResponseSchema:
    """
    Get a topic by ID
    """
    return await controller.get_topic(topic_id)


@router.post("/{topic_id}/image", response_model=TopicResponseSchema)
async def upload_topic_image(
    topic_id: int,
    file: UploadFile = File(...),
    user_uuid: Annotated[str, Depends(get_current_user_uuid)] = None,
    controller: TopicsController = Depends()
) -> TopicResponseSchema:
    """
    Upload image for a topic
    """
    return await controller.upload_topic_image(topic_id, file, user_uuid)


@router.delete("/{topic_id}/image", response_model=TopicResponseSchema)
async def delete_topic_image(
    topic_id: int,
    user_uuid: Annotated[str, Depends(get_current_user_uuid)] = None,
    controller: TopicsController = Depends()
) -> TopicResponseSchema:
    """
    Delete image from a topic
    """
    return await controller.delete_topic_image(topic_id, user_uuid)
