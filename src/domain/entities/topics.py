"""
Topics entity
"""

from datetime import datetime
from dataclasses import dataclass


@dataclass
class TopicEntity:
    """
    Topic entity
    """

    id: int
    title: str
    qtd_posts: int
    description: str
    topic_image_id: int
    created_by_user_id: int
    created_at: datetime
