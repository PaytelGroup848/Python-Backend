from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.training_runtime.providers.runtime_factory import (
    training_runtime_factory,
)

from app.modules.training_runtime.services.training_data_runtime_service import (
    training_data_runtime_service,
)

from app.modules.training_runtime.services.training_runtime_service import (
    training_runtime_service,
)

from app.modules.training_runtime.schemas.training_result_schema import (
    TrainingResult,
)


class TrainingExecutorService:

    async def execute(
        self,
        db: AsyncSession,
        training_job_id: int,
    ) -> TrainingResult:

        runtime = await (
            training_runtime_service
            .load_runtime(
                db=db,
                training_job_id=training_job_id,
            )
        )

        batch_size = (
            runtime.runtime_configuration
            .get(
                "data_batch_size"
            )
        )

        if batch_size is None:
            raise ValueError(
                "Training configuration must define "
                "'data_batch_size'."
            )

        if (
            isinstance(batch_size, bool)
            or
            not isinstance(batch_size, int)
            or
            batch_size <= 0
        ):
            raise ValueError(
                "'data_batch_size' must be a positive integer."
            )

        training_data = await (
            training_data_runtime_service
            .open_snapshot_stream(
                db=db,
                dataset_snapshot_id=(
                    runtime.dataset_snapshot_id
                ),
                batch_size=batch_size,
            )
        )

        training_runtime = (
            training_runtime_factory
            .get_runtime(
                runtime.runtime_class
            )
        )

        return await (
            training_runtime
            .execute(
                runtime=runtime,
                training_data=training_data,
            )
        )


training_executor_service = (
    TrainingExecutorService()
)