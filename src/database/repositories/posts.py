"""
Posts repository
"""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload

from domain.repositories import IPostRepository
from domain.entities import PostEntity, BlobEntity
from ..models import PostModel



class PostRepository(IPostRepository):
    """
    Topics repository
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, post: PostEntity):
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
            select(PostModel)
            .where(PostModel.id == post_id)
            .options(joinedload(PostModel.anexos))
        )

        result = await self.session.exec(statement)
        model = result.one()

        return self._model_to_entity(model)

    async def update(self, post: PostEntity):
        """
        Update a post
        """

        model = self._entity_to_model(post)
        self.session.add(model)
        await self.session.flush()

        return model

    def _entity_to_model(self, entity: PostEntity) -> PostModel:
        """
        Convert a PostEntity to a PostModel
        """

        return PostModel(
            id=entity.id,
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
