from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.ingestion.models.ingestion_job import (
    IngestionJob
)

from app.modules.ingestion.schemas.ingestion_job_create import (
    IngestionJobCreate
)

from app.modules.ingestion.repositories.ingestion_job_repository import (
    ingestion_job_repository
)


class IngestionJobService:

    async def create_ingestion_job(

        self,

        db: AsyncSession,

        data: IngestionJobCreate

    ):

        ingestion_job = IngestionJob(

            **data.model_dump()

        )

        return await (

            ingestion_job_repository
            .create(
                db,
                ingestion_job
            )
        )

    async def get_ingestion_job(

        self,

        db: AsyncSession,

        ingestion_job_id: int

    ):

        return await (

            ingestion_job_repository
            .get_by_id(
                db,
                ingestion_job_id
            )
        )

    async def list_by_dataset(

        self,

        db: AsyncSession,

        dataset_id: int

    ):

        return await (

            ingestion_job_repository
            .list_by_dataset(
                db,
                dataset_id
            )
        )

    async def list_by_source(

        self,

        db: AsyncSession,

        corpus_source_id: int

    ):

        return await (

            ingestion_job_repository
            .list_by_source(
                db,
                corpus_source_id
            )
        )
    
    async def list_by_status(

        self,

        db: AsyncSession,

        status: str

    ):

        return await (

            ingestion_job_repository
            .list_by_status(
                db,
                status
            )
        )


ingestion_job_service = (
    IngestionJobService()
)