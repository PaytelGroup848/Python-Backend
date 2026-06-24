from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.dataset_builder.schemas.dataset_build_runtime import (
    DatasetBuildRuntime
)

from app.modules.ingestion.repositories.ingestion_job_repository import (
    ingestion_job_repository
)

from app.modules.datasets.repositories.dataset_repository import (
    dataset_repository
)

from app.modules.corpora.repositories.corpus_source_repository import (
    corpus_source_repository
)


class DatasetBuildRuntimeService:

    async def build_runtime(

        self,

        db: AsyncSession,

        ingestion_job_id: int

    ) -> DatasetBuildRuntime:

        ingestion_job = await (

            ingestion_job_repository
            .get_by_id(
                db,
                ingestion_job_id
            )
        )

        if not ingestion_job:

            raise ValueError(
                "Ingestion job not found"
            )

        dataset = await (

            dataset_repository
            .get_by_id(
                db,
                ingestion_job.dataset_id
            )
        )

        if not dataset:

            raise ValueError(
                "Dataset not found"
            )

        corpus_source = await (

            corpus_source_repository
            .get_by_id(
                db,
                ingestion_job.corpus_source_id
            )
        )

        if not corpus_source:

            raise ValueError(
                "Corpus source not found"
            )

        return DatasetBuildRuntime(

            ingestion_job_id=ingestion_job.id,

            dataset_id=dataset.id,

            corpus_source_id=corpus_source.id,

            status=ingestion_job.status
        )


dataset_build_runtime_service = (
    DatasetBuildRuntimeService()
)