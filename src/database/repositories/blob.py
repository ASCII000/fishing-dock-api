"""
Blob repository
"""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from domain.repositories import IBlobRepository
from domain.entities import BlobEntity
from ..models import BlobModel


class BlobRepository(IBlobRepository):
    """
    Blob repository
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_file(self, file_id: str) -> BlobEntity:
        """
        Method for get file from storage

        Args:
            file_id: str

        Returns:
            BlobEntity: The file entity
        """

        statement = select(BlobModel).where(BlobModel.id == file_id)
        result = await self.session.exec(statement)
        blob_model = result.one_or_none()

        if not blob_model:
            return None

        return self._model_to_entity(blob_model)

    async def save(self, file: BlobEntity) -> BlobEntity:
        """
        Method for upload file to storage

        Args:
            file: BlobEntity

        Returns:
            BlobEntity: The uploaded file entity
        """

        model = self._entity_to_model(file)
        self.session.add(model)
        await self.session.flush()

        return self._model_to_entity(model)

    def _model_to_entity(self, model: BlobModel) -> BlobEntity:
        """
        Convert a BlobModel to a BlobEntity
        """

        return BlobEntity(
            id=model.id,
            provedor=model.provedor,
            provedor_id=model.provedor_id,
            link=model.link,
            nome=model.nome,
            extensao=model.extensao,
            criado_em=model.criado_em,
        )

    def _entity_to_model(self, entity: BlobEntity) -> BlobModel:
        """
        Convert a BlobEntity to a BlobModel
        """

        return BlobModel(
            id=entity.id,
            provedor=entity.provedor,
            provedor_id=entity.provedor_id,
            link=entity.link,
            nome=entity.nome,
            extensao=entity.extensao,
        )
    