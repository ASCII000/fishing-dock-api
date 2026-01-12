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
    imagem_perfil: str = Field(max_length=300)
    senha: str
