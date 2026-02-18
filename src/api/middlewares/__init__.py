"""
Setup Middlewares Fastapi
"""

import jwt

from fastapi import FastAPI

from domain.exceptions import SecurityError, NotFoundException, DuplicateException
from ._exec.integrations import blob_storage_exception_handler, BlobStorageException
from ._exec.exception_handlers import (
    security_error_handler,
    not_found_handler,
    duplicate_handler,
    jwt_error_handler,
    jwt_expired_handler,
)


def setup_middlewares(app: FastAPI):
    """
    Setup middlewares and exception handlers
    """
    # Integration exception handlers
    app.add_exception_handler(BlobStorageException, blob_storage_exception_handler)

    # Domain exception handlers
    app.add_exception_handler(SecurityError, security_error_handler)
    app.add_exception_handler(NotFoundException, not_found_handler)
    app.add_exception_handler(DuplicateException, duplicate_handler)

    # JWT exception handlers
    app.add_exception_handler(jwt.InvalidTokenError, jwt_error_handler)
    app.add_exception_handler(jwt.ExpiredSignatureError, jwt_expired_handler)