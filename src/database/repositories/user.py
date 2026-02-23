"""
User repository
"""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload

from domain.repositories import IUserRepository
from domain.entities import UserEntity, BlobEntity
from ..models import UserModel


class UserRepository(IUserRepository):
    """
    Repository for user
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str):
        """
        Get user by email
        """

        statement = (
            select(UserModel)
            .where(UserModel.email == email)
            .options(joinedload(UserModel.avatar_blob))
        )
        user = await self.session.exec(statement)
        user = user.unique().one_or_none()
        if not user:
            return None

        return self._model_to_entity(user, include_avatar=True)

    async def get_by_uuid(self, uuid: str):
        """
        Get user by uuid
        """

        statement = (
            select(UserModel)
            .where(UserModel.uuid == uuid)
            .options(joinedload(UserModel.avatar_blob))
        )
        user = await self.session.exec(statement)
        user = user.unique().one_or_none()
        if not user:
            return None

        return self._model_to_entity(user, include_avatar=True)

    async def create(self, user: UserEntity):
        """
        Create a new user
        """

        model = self._entity_to_model(user)
        self.session.add(model)
        await self.session.flush()

        return self._model_to_entity(model)

    async def update_user(self, user: UserEntity):
        """
        Updated user
        """
        statement = (
            select(UserModel)
            .where(UserModel.id == user.uuid)
            .options(joinedload(UserModel.avatar_blob))
        )
        result = await self.session.exec(statement)
        model = result.unique().one_or_none()

        if model is None:
            return None

        model.nome = user.nome
        model.email = user.email
        model.telefone = user.telefone
        model.avatar_blob_id = user.avatar_blob_id
        model.ativo = user.ativo
        model.excluido = user.excluido
        model.senha = user.get_password_hash()

        await self.session.flush()
        return self._model_to_entity(model, include_avatar=True)

    def _model_to_entity(self, model: UserModel, include_avatar: bool = False) -> UserEntity:
        """
        Helper method for convert model to entity

        Args:
            model: UserModel to convert
            include_avatar: Whether to include avatar blob (requires eager loading)
        """
        avatar = None
        if include_avatar and model.avatar_blob_id and model.avatar_blob:
            avatar = BlobEntity(
                id=model.avatar_blob.id,
                link=model.avatar_blob.link,
                criado_em=model.avatar_blob.criado_em,
                extensao=model.avatar_blob.extensao,
                nome=model.avatar_blob.nome,
                provedor=model.avatar_blob.provedor,
                provedor_id=model.avatar_blob.provedor_id,
            )

        return UserEntity(
            id=model.id,
            nome=model.nome,
            ativo=model.ativo,
            email=model.email,
            excluido=model.excluido,
            telefone=model.telefone,
            uuid=model.uuid,
            avatar=avatar,
            avatar_blob_id=model.avatar_blob_id,
            _senha_hash=model.senha,
        )

    def _entity_to_model(self, entity: UserEntity) -> UserModel:
        """
        Helper method for convert entity to model
        """

        return UserModel(
            nome=entity.nome,
            ativo=entity.ativo,
            email=entity.email,
            avatar_blob_id=entity.avatar_blob_id,
            excluido=entity.excluido,
            telefone=entity.telefone,
            uuid=entity.uuid,
            senha=entity.get_password_hash(),
        )
