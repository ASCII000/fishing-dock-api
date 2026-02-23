"""
Topics repository
"""

from typing import List, Optional, Tuple

from sqlmodel import select, update, func, or_
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload

from domain.repositories import ITopicRepository
from domain.entities import TopicEntity
from ..models import TopicModel



class TopicRepository(ITopicRepository):
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
        model = result.unique().one_or_none()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def update(self, post: TopicEntity):
        """
        Update a post
        """

        model = self._entity_to_model(post)
        self.session.add(model)
        await self.session.flush()

        return model

    async def increment_post_count(self, topic_id: int, quantity: int) -> None:
        """
        Increment post count for a topic
        """

        statement = (
            update(TopicModel)
            .where(TopicModel.id == topic_id)
            .values(quantidade_posts=TopicModel.quantidade_posts + quantity)
        )

        await self.session.exec(statement)

    async def search(
        self,
        search: Optional[str],
        page: int,
        items_per_page: int
    ) -> Tuple[List[TopicEntity], int]:
        """
        Search topics by title or id with pagination
        """
        # Base query
        base_query = select(TopicModel)

        # Apply search filter if provided
        if search:
            # Check if search is numeric (could be an ID)
            if search.isdigit():
                base_query = base_query.where(
                    or_(
                        TopicModel.id == int(search),
                        TopicModel.titulo.ilike(f"%{search}%")
                    )
                )
            else:
                base_query = base_query.where(
                    TopicModel.titulo.ilike(f"%{search}%")
                )

        # Count total results
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.exec(count_query)
        total_count = count_result.one()

        # Apply pagination and ordering
        offset = (page - 1) * items_per_page
        paginated_query = (
            base_query
            .options(joinedload(TopicModel.topico_thumbnail_blob))
            .order_by(TopicModel.criado_em.desc())
            .offset(offset)
            .limit(items_per_page)
        )

        result = await self.session.exec(paginated_query)
        models = result.unique().all()

        return [self._model_to_entity(model) for model in models], total_count

    def _entity_to_model(self, entity: TopicEntity) -> TopicModel:
        """
        Convert a PostEntity to a PostModel
        """

        return TopicModel(
            id=entity.id if entity.id else None,
            titulo=entity.title,
            descricao=entity.description,
            criado_em=entity.created_at,
            criado_por_id=entity.created_by_user_id,
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
