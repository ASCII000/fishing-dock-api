"""
Posts entity
"""

from typing import Optional, List
from dataclasses import dataclass, field

from .blob import BlobEntity


@dataclass
class PostEntity:
    """
    Post entity
    """

    id: int
    title: str
    description: str
    user_id: int
    reply_post_id: Optional[int]
    likes_count: int
    reply_count: int
    topic_post_id: int
    post_apppends: List[BlobEntity] = field(default_factory=list)
    _removed_append_ids: List[int] = field(default_factory=list)


    def remove_append(self, append_id: int) -> None:
        """
        Remove append
        """
        original_length = len(self.post_apppends)

        self.post_apppends = [
            x for x in self.post_apppends if x.id != append_id
        ]

        if len(self.post_apppends) != original_length:
            self._removed_append_ids.append(append_id)

    def get_removed_append_ids(self) -> List[int]:
        """
        Get removed append ids
        """
        return self._removed_append_ids
