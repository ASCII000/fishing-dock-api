# pylint: disable=not-callable

"""
Models the database
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime, func



class BlobModel(SQLModel, table=True):
    """
    Blob model
    """

    __tablename__ = "arquivos_blob"

    id: int = Field(default=None, primary_key=True)
    provedor: str = Field(max_length=50)
    provedor_id: str = Field(max_length=100)
    link: Optional[str] = Field(max_length=300)
    nome: str = Field(max_length=150)
    extensao: str = Field(max_length=10)
    criado_em: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, server_default=func.now(), nullable=False),
    )


class UserModel(SQLModel, table=True):
    """
    User model
    """

    __tablename__ = "usuarios"

    id: int = Field(default=None, primary_key=True)
    nome: str = Field(max_length=150)
    email: str = Field(max_length=128)
    uuid: str = Field(max_length=36)
    avatar_blob_id: Optional[int] = Field(default=None, foreign_key="arquivos_blob.id")
    avatar_blob: Optional[BlobModel] = Relationship()
    telefone: str = Field(max_length=11)
    ativo: bool = Field(default=True)
    excluido: bool = Field(default=False)
    senha: str = Field(max_length=256, description="HASH256 da senha")
    criado_em: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, server_default=func.now(), nullable=False),
    )
