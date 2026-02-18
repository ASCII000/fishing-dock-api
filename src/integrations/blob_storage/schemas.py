"""
Schemas for blob storage
"""

from datetime import datetime

from pydantic import BaseModel, Field


class FileSchema(BaseModel):
    """
    Blob storage schema
    """
    id: str = Field(..., description="File ID")
    name: str = Field(..., description="Filename")
    link: str = Field(..., description="Link")
    created_at: datetime = Field(..., description="Created at")
