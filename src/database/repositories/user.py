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
        user = user.one_or_none()
        if not user:
            return None

        return self._model_to_entity(user)

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
        user = user.one_or_none()
        if not user:
            return None

        return self._model_to_entity(user)

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
        model = result.one()

        model.nome = user.nome
        model.email = user.email
        model.telefone = user.telefone
        model.avatar_url = user.avatar_url
        model.ativo = user.ativo
        model.excluido = user.excluido
        model.senha = user.get_password_hash()

        await self.session.flush()
        return self._model_to_entity(model)

    def _model_to_entity(self, model: UserModel) -> UserEntity:
        """
        Helper method for convert model to entity
        """

        return UserEntity(
            nome=model.nome,
            ativo=model.ativo,
            email=model.email,
            excluido=model.excluido,
            telefone=model.telefone,
            uuid=model.uuid,
            avatar=BlobEntity(
                id=model.avatar_blob_id,
                link=model.avatar_blob.link,
                criado_em=model.avatar_blob.criado_em,
                extensao=model.avatar_blob.extensao,
                nome=model.avatar_blob.nome,
                provedor=model.avatar_blob.provedor,
                provedor_id=model.avatar_blob.provedor_id,
            ) if model.avatar_blob else None,
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
