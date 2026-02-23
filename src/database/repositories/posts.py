"""
Posts repository
"""

from typing import List, Optional, Tuple

from sqlmodel import select, update, func, or_
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload

from domain.repositories import IPostRepository
from domain.entities import PostEntity, BlobEntity
from ..models import PostModel, PostsAppendModel, BlobModel



class PostRepository(IPostRepository):
    """
    Topics repository
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, topic_id: int, user_id: int, post: PostEntity):
        """
        Create a new post
        """
        post.topic_post_id = topic_id
        post.user_id = user_id

        model = self._entity_to_model(post)
        self.session.add(model)
        await self.session.flush()

        # Create attachments in posts_anexos table
        if post.post_apppends:
            for blob in post.post_apppends:
                append_model = PostsAppendModel(
                    post_id=model.id,
                    anexo_blob_id=blob.id
                )
                self.session.add(append_model)
            await self.session.flush()

        return model


    async def get_by_id(self, post_id: int):
        """
        Get post by id
        """

        statement = (
            select(PostModel)
            .where(PostModel.id == post_id)
            .options(
                joinedload(PostModel.anexos).joinedload(PostsAppendModel.anexo_blob)
            )
        )

        result = await self.session.exec(statement)
        model = result.unique().one_or_none()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def update(self, post: PostEntity):
        """
        Update a post
        """

        model = self._entity_to_model(post)
        self.session.add(model)
        await self.session.flush()

        return model


    async def increment_reply_count(self, post_id: int, quantity: int) -> None:
        """
        Increment reply count for a post
        """

        statement = (
            update(PostModel)
            .where(PostModel.id == post_id)
            .values(resposta_contador=PostModel.resposta_contador + quantity)
        )

        await self.session.exec(statement)

    async def add_appends(self, post_id: int, blobs: List[BlobEntity]) -> None:
        """
        Add appends to a post
        """
        for blob in blobs:
            append_model = PostsAppendModel(
                post_id=post_id,
                anexo_blob_id=blob.id
            )
            self.session.add(append_model)
        await self.session.flush()

    async def search(
        self,
        topic_id: int,
        search: Optional[str],
        page: int,
        items_per_page: int
    ) -> Tuple[List[PostEntity], int]:
        """
        Search posts by title or id with pagination
        """
        # Base query - filter by topic_id
        base_query = select(PostModel).where(PostModel.topico_post_id == topic_id)

        # Apply search filter if provided
        if search:
            if search.isdigit():
                base_query = base_query.where(
                    or_(
                        PostModel.id == int(search),
                        PostModel.titulo.ilike(f"%{search}%")
                    )
                )
            else:
                base_query = base_query.where(
                    PostModel.titulo.ilike(f"%{search}%")
                )

        # Count total results
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.exec(count_query)
        total_count = count_result.one()

        # Apply pagination and ordering
        offset = (page - 1) * items_per_page
        paginated_query = (
            base_query
            .options(
                joinedload(PostModel.anexos).joinedload(PostsAppendModel.anexo_blob)
            )
            .order_by(PostModel.criado_em.desc())
            .offset(offset)
            .limit(items_per_page)
        )

        result = await self.session.exec(paginated_query)
        models = result.unique().all()

        return [self._model_to_entity(model) for model in models], total_count

    def _entity_to_model(self, entity: PostEntity) -> PostModel:
        """
        Convert a PostEntity to a PostModel
        """

        return PostModel(
            id=entity.id if entity.id else None,
            titulo=entity.title,
            descricao=entity.description,
            usuario_id=entity.user_id,
            resposta_post_id=entity.reply_post_id,
            topico_post_id=entity.topic_post_id,
            gostei_contador=entity.likes_count,
            resposta_contador=entity.reply_count,
        )

    def _model_to_entity(self, model: PostModel) -> PostEntity:
        """
        Convert a PostModel to a PostEntity
        """

        return PostEntity(
            id=model.id,
            title=model.titulo,
            description=model.descricao,
            user_id=model.usuario_id,
            reply_post_id=model.resposta_post_id,
            likes_count=model.gostei_contador,
            reply_count=model.resposta_contador,
            topic_post_id=model.topico_post_id,
            post_apppends=[
                BlobEntity(
                    id=blob.anexo_blob.id,
                    link=blob.anexo_blob.link,
                    criado_em=blob.anexo_blob.criado_em,
                    extensao=blob.anexo_blob.extensao,
                    nome=blob.anexo_blob.nome,
                    provedor=blob.anexo_blob.provedor,
                    provedor_id=blob.anexo_blob.provedor_id,
                ) for blob in model.anexos
            ]
        )
