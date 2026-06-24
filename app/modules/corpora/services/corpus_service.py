from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.corpora.models.corpus import (
    Corpus
)

from app.modules.corpora.repositories.corpus_repository import (
    corpus_repository
)

from app.modules.corpora.schemas.corpus_create import (
    CorpusCreate
)


class CorpusService:

    async def create_corpus(

        self,

        db: AsyncSession,

        data: CorpusCreate

    ):

        corpus = Corpus(
            **data.model_dump()
        )

        return await (
            corpus_repository
            .create(
                db,
                corpus
            )
        )

    async def get_corpus(

        self,

        db: AsyncSession,

        corpus_id: int

    ):

        return await (
            corpus_repository
            .get_by_id(
                db,
                corpus_id
            )
        )

    async def list_corpora(

        self,

        db: AsyncSession

    ):

        return await (
            corpus_repository
            .list_all(
                db
            )
        )


corpus_service = (
    CorpusService()
)