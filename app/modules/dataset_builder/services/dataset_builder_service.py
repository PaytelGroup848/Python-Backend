from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.datasets.repositories.dataset_repository import (
    dataset_repository
)

from app.modules.dataset_records.repositories.dataset_record_repository import (
    dataset_record_repository
)

from app.modules.data_pipelines.repositories.data_pipeline_repository import (
    data_pipeline_repository
)

from app.modules.pipeline_runtime.services.pipeline_runtime_service import (
    pipeline_runtime_service,
)

from app.modules.dataset_builder.schemas.dataset_builder_response import (
    DatasetBuilderResponse,
    DatasetBuilderSummary,
    DatasetBuilderConfiguration,
)

from app.modules.dataset_builder.schemas.dataset_build_response import (
    DatasetBuildResponse,
)


class DatasetBuilderService:

    async def get_builder(
        self,
        db: AsyncSession,
        dataset_id: int,
    ):

        dataset = await (
            dataset_repository.get_by_id(
                db,
                dataset_id,
            )
        )

        if dataset is None:

            raise ValueError(
                "Dataset not found."
            )

        total_records = await (
            dataset_record_repository.count_by_dataset(
                db=db,
                dataset_id=dataset_id,
            )
        )

        summary = DatasetBuilderSummary(

            dataset_id=dataset.id,

            dataset_name=dataset.name,

            dataset_version=dataset.version,

            dataset_status=dataset.status,

            total_records=total_records,

            valid_records=total_records,

            invalid_records=0,

            duplicate_records=0,

            build_status="READY",

            last_build_at=None,

            created_at=dataset.created_at,

            updated_at=dataset.updated_at,

        )

        configuration = DatasetBuilderConfiguration(

            dataset_id=dataset.id,

            train_split=0.8,

            validation_split=0.1,

            test_split=0.1,

            shuffle=True,

            random_seed=None,

        )

        return DatasetBuilderResponse(

            summary=summary,

            configuration=configuration,

            validation=[],

            preview=[],

        )

    async def build_dataset(
        self,
        db: AsyncSession,
        dataset_id: int,
        pipeline_id: int
    ):

        dataset = (
            await dataset_repository.get_by_id(
                db,
                dataset_id
            )
        )

        if not dataset:

            raise ValueError(
                "Dataset not found"
            )

        pipeline = (
            await data_pipeline_repository.get_by_id(
                db,
                pipeline_id
            )
        )

        if not pipeline:

            raise ValueError(
                "Pipeline not found"
            )

        total_records = await (
            dataset_record_repository.count_by_dataset(
                db=db,
                dataset_id=dataset_id,
            )
        )

        pipeline_result = await (
            pipeline_runtime_service.execute_pipeline(
                db=db,
                dataset_id=dataset.id,
                pipeline_id=pipeline.id,
            )
        )

        processed_records = (
            pipeline_result.processed_records
        )

        failed_records = (
            pipeline_result.failed_records
        )

        dataset.status = "READY"

        await dataset_repository.update(
            db=db,
            entity=dataset,
        )


        

        return DatasetBuildResponse(

            dataset_id=dataset_id,

            pipeline_id=pipeline_id,

            total_records=total_records,

            processed_records=processed_records,

            failed_records=failed_records,

            status="completed",

        )


dataset_builder_service = (
    DatasetBuilderService()
)