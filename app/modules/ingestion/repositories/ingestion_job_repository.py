from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.ingestion.models.ingestion_job import (
    IngestionJob
)


class IngestionJobRepository:

    async def create(

        self,

        db: AsyncSession,

        ingestion_job: IngestionJob

    ):

        db.add(
            ingestion_job
        )

        await db.flush()

        await db.refresh(
            ingestion_job
        )

        return ingestion_job

    async def get_by_id(

        self,

        db: AsyncSession,

        ingestion_job_id: int

    ):

        result = await db.execute(

            select(
                IngestionJob
            )
            .where(
                IngestionJob.id
                ==
                ingestion_job_id
            )
        )

        return result.scalar_one_or_none()

    async def list_by_dataset(

        self,

        db: AsyncSession,

        dataset_id: int

    ):

        result = await db.execute(

            select(
                IngestionJob
            )
            .where(
                IngestionJob.dataset_id
                ==
                dataset_id
            )
        )

        return result.scalars().all()

    async def list_by_source(

        self,

        db: AsyncSession,

        corpus_source_id: int

    ):

        result = await db.execute(

            select(
                IngestionJob
            )
            .where(
                IngestionJob.corpus_source_id
                ==
                corpus_source_id
            )
        )

        return result.scalars().all()
    
    async def list_by_status(

        self,

        db: AsyncSession,

        status: str

    ):

        result = await db.execute(

            select(
                IngestionJob
            )
            .where(
                IngestionJob.status
                ==
                status
            )
        )

        return result.scalars().all()

    async def update(

        self,

        db: AsyncSession,

        ingestion_job: IngestionJob

    ):

        await db.flush()

        await db.refresh(
            ingestion_job
        )

        return ingestion_job


ingestion_job_repository = (
    IngestionJobRepository()
)