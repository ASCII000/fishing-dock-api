"""
Register schemas
"""

from pydantic import BaseModel, Field


class UserRequestSchema(BaseModel):
    """
    User request schema
    """
    nome: str = Field(max_length=150)
    email: str = Field(max_length=128)
    telefone: str = Field(max_length=11)
    senha: str


class UserResponseSchema(BaseModel):
    """
    User response schema
    """
    nome: str
    email: str
    avatar: str
    telefone: str
