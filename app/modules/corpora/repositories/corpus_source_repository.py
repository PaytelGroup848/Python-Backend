from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.corpora.models.corpus_source import (
    CorpusSource
)


class CorpusSourceRepository:

    async def create(

        self,

        db: AsyncSession,

        corpus_source: CorpusSource

    ):

        db.add(
            corpus_source
        )

        await db.flush()

        await db.refresh(
            corpus_source
        )

        return corpus_source

    async def get_by_id(

        self,

        db: AsyncSession,

        corpus_source_id: int

    ):

        result = await db.execute(

            select(
                CorpusSource
            )
            .where(
                CorpusSource.id
                ==
                corpus_source_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_reference(

        self,

        db: AsyncSession,

        corpus_id: int,

        connector_instance_id: int,

        source_reference: str

    ):

        result = await db.execute(

            select(
                CorpusSource
            )
            .where(
                CorpusSource.corpus_id
                ==
                corpus_id,

                CorpusSource.connector_instance_id
                == connector_instance_id,

                CorpusSource.source_reference
                ==
                source_reference
            )
        )

        return result.scalar_one_or_none()

    async def list_by_corpus(

        self,

        db: AsyncSession,

        corpus_id: int

    ):

        result = await db.execute(

            select(
                CorpusSource
            )
            .where(
                CorpusSource.corpus_id
                ==
                corpus_id
            )
        )

        return result.scalars().all()

    async def update(

        self,

        db: AsyncSession,

        corpus_source: CorpusSource

    ):

        await db.flush()

        await db.refresh(
            corpus_source
        )

        return corpus_source


corpus_source_repository = (
    CorpusSourceRepository()
)