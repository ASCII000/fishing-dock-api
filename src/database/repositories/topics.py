"""
Topics repository
"""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload

from domain.repositories import IPostRepository
from domain.entities import TopicEntity
from ..models import TopicModel



class TopicRepository(IPostRepository):
    """
    Topics repository
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, post: TopicEntity):
        """
        Create a new post
        """

        model = self._entity_to_model(post)
        self.session.add(model)
        await self.session.flush()

        return model


    async def get_by_id(self, post_id: int):
        """
        Get post by id
        """

        statement = (
            select(TopicModel)
            .where(TopicModel.id == post_id)
            .options(joinedload(TopicModel.topico_thumbnail_blob))
        )

        result = await self.session.exec(statement)
        model = result.one()

        return self._model_to_entity(model)

    async def update(self, post: TopicEntity):
        """
        Update a post
        """

        model = self._entity_to_model(post)
        self.session.add(model)
        await self.session.flush()

        return model

    def _entity_to_model(self, entity: TopicEntity) -> TopicModel:
        """
        Convert a PostEntity to a PostModel
        """

        return TopicModel(
            id=entity.id,
            titulo=entity.title,
            descricao=entity.description,
            criado_em=entity.created_at,
            topico_thumbnail_blob_id=entity.topic_image_id,
            quantidade_posts=entity.qtd_posts,
        )

    def _model_to_entity(self, model: TopicModel) -> TopicEntity:
        """
        Convert a PostModel to a PostEntity
        """

        return TopicEntity(
            created_at=model.criado_em,
            created_by_user_id=model.criado_por_id,
            description=model.descricao,
            id=model.id,
            qtd_posts=model.quantidade_posts,
            title=model.titulo,
            topic_image_id=model.topico_thumbnail_blob_id
        )
