"""
Domain interfaces
"""

from .blob_storage import IBlobStorageProvider, BlobUploadResult


__all__ = [
    "IBlobStorageProvider",
    "BlobUploadResult",
]
