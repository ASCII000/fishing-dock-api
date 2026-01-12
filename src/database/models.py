"""
Models the database
"""

from typing import Optional

from sqlmodel import Field, SQLModel


class UserModel(SQLModel, table=True):
    """
    User model
    """

    __tablename__ = "usuarios"

    id: int = Field(default=None, primary_key=True)
    nome: str = Field(max_length=150)
    email: str = Field(max_length=128)
    uuid: str = Field(max_length=36)
    imagem_perfil: Optional[str] = Field(max_length=300)
    telefone: str = Field(max_length=11)
    ativo: bool = Field(default=True)
    excluido: bool = Field(default=False)
    senha: str = Field(max_length=256, description="HASH256 da senha")
