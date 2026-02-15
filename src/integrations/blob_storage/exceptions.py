"""
Blob storage major exceptions
"""

from typing import Any


class BlobStorageException(Exception):
    """
    Base blob storage exception
    """
    def __init__(
        self,
        message: str,
        detail: Any,
        code: int,
        *args
    ):
        self.message = message
        self.detail = detail
        self.code = code
        super().__init__(*args)
