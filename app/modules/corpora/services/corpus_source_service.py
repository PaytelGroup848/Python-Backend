from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.corpora.models.corpus_source import (
    CorpusSource
)

from app.modules.corpora.repositories.corpus_source_repository import (
    corpus_source_repository
)

from app.modules.corpora.schemas.corpus_source_create import (
    CorpusSourceCreate
)


class CorpusSourceService:

    async def create_source(

        self,

        db: AsyncSession,

        data: CorpusSourceCreate

    ):

        corpus_source = CorpusSource(
            **data.model_dump()
        )

        return await (
            corpus_source_repository
            .create(
                db,
                corpus_source
            )
        )

    async def get_source(

        self,

        db: AsyncSession,

        source_id: int

    ):

        return await (
            corpus_source_repository
            .get_by_id(
                db,
                source_id
            )
        )

    async def get_corpus_sources(

        self,

        db: AsyncSession,

        corpus_id: int

    ):

        return await (
            corpus_source_repository
            .get_by_corpus(
                db,
                corpus_id
            )
        )


corpus_source_service = (
    CorpusSourceService()
)