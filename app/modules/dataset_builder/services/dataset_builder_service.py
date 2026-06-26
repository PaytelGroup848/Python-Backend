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


class DatasetBuilderService:

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

        records = (
            await dataset_record_repository.list_by_dataset(
                db,
                dataset_id
            )
        )

        total_records = len(
            records
        )

        processed_records = 0

        failed_records = 0

        for record in records:

            try:

                processed_records += 1

            except Exception:

                failed_records += 1

        dataset.status = "ready"

        await dataset_repository.update(
            db,
            dataset
        )

        return {

            "dataset_id": dataset_id,

            "pipeline_id": pipeline_id,

            "total_records": total_records,

            "processed_records": processed_records,

            "failed_records": failed_records,

            "status": "completed"
        }


dataset_builder_service = (
    DatasetBuilderService()
)