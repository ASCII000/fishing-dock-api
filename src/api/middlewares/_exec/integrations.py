"""
Integration Middleware error tratment
"""

from loguru import logger

from fastapi import status
from fastapi.exceptions import HTTPException

from integrations.blob_storage.exceptions import BlobStorageException


def blob_storage_exception_handler(_, exc: BlobStorageException):
    """
    Blob storage exception handler
    """

    logger.error(exc.message, detail=exc.detail, code=exc.code)
    raise HTTPException(
        detail="Problemas com o armazenamento de arquivos, tente novamente mais tarde",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
