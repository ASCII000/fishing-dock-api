# pylint: disable=not-callable

"""
Models the database
"""

from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime, func, Integer



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


class PostModel(SQLModel, table=True):
    """
    Post model
    """

    __tablename__ = "posts"

    id: int = Field(default=None, primary_key=True)
    titulo: str = Field(max_length=150)
    descricao: str = Field(max_length=300)
    usuario_id: int = Field(foreign_key="usuarios.id")
    resposta_post_id: Optional[int] = Field(default=None, foreign_key="posts.id")
    usuario: Optional[UserModel] = Relationship()
    resposta_post: Optional["PostModel"] = Relationship(
        sa_relationship_kwargs={"remote_side": "PostModel.id"}
    )
    anexos: List["PostsAppendModel"] = Relationship(back_populates="post")
    topico_post_id: int = Field(foreign_key="topicos.id")
    gostei_contador: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    resposta_contador: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    criado_em: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, server_default=func.now(), nullable=False),
    )


class PostsAppendModel(SQLModel, table=True):
    """
    Posts append model
    """

    __tablename__ = "posts_anexos"

    id: int = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="posts.id")
    post: Optional[PostModel] = Relationship(back_populates="anexos")
    anexo_blob_id: int = Field(foreign_key="arquivos_blob.id")
    anexo_blob: Optional[BlobModel] = Relationship()
    criado_em: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, server_default=func.now(), nullable=False),
    )


class TopicModel(SQLModel, table=True):
    """
    Topic model
    """

    __tablename__ = "topicos"

    id: int = Field(default=None, primary_key=True)
    titulo: str = Field(max_length=150)
    descricao: str = Field(max_length=300)
    quantidade_posts: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    topico_thumbnail_blob_id: Optional[int] = Field(default=None, foreign_key="arquivos_blob.id")
    topico_thumbnail_blob: Optional[BlobModel] = Relationship()
    criado_por_id: int = Field(foreign_key="usuarios.id")
    criado_em: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, server_default=func.now(), nullable=False),
    )
