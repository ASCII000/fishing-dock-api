"""
Setup Middlewares Fastapi
"""

from fastapi import FastAPI

from ._exec.integrations import blob_storage_exception_handler, BlobStorageException


def setup_middlewares(app: FastAPI):
    """
    Setup middlewares Fastapi 
    """
    app.add_exception_handler(BlobStorageException, blob_storage_exception_handler)