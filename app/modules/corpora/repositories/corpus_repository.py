from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.corpora.models.corpus import (
    Corpus
)


class CorpusRepository:

    async def create(

        self,

        db: AsyncSession,

        corpus: Corpus

    ):

        db.add(
            corpus
        )

        await db.flush()

        await db.refresh(
            corpus
        )

        return corpus

    async def get_by_id(

        self,

        db: AsyncSession,

        corpus_id: int

    ):

        result = await db.execute(

            select(
                Corpus
            )
            .where(
                Corpus.id
                ==
                corpus_id
            )
        )

        return result.scalar_one_or_none()

    async def list_all(

        self,

        db: AsyncSession

    ):

        result = await db.execute(

            select(
                Corpus
            )
        )

        return result.scalars().all()

    async def update(

        self,

        db: AsyncSession,

        corpus: Corpus

    ):

        await db.flush()

        await db.refresh(
            corpus
        )

        return corpus


corpus_repository = (
    CorpusRepository()
)