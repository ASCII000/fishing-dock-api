"""
Login Schemas
"""

from pydantic import BaseModel, Field


class UserTokensResponseSchema(BaseModel):
    """
    User response schema
    """
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")

