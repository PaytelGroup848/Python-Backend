from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.training.repositories.training_job_repository import (
    training_job_repository
)

from app.modules.datasets.repositories.dataset_repository import (
    dataset_repository
)

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime
)

from app.modules.training_providers.repositories.training_provider_repository import (
    training_provider_repository
)


class TrainingRuntimeService:

    async def load_runtime(

        self,

        db: AsyncSession,

        training_job_id: int

    ) -> TrainingRuntime:

        job = await (
            training_job_repository
            .get_by_id(
                db,
                training_job_id
            )
        )

        if not job:

            raise ValueError(
                "Training job not found"
            )
        
        provider = await (
            training_provider_repository
            .get_by_id(
                db,
                job.training_provider_id
            )
        )

        if not provider:

            raise ValueError(
                "Training provider not found"
            )
        if not provider.is_active:

            raise ValueError(
                "Training provider is inactive"
            )

        dataset = await (
            dataset_repository
            .get_by_id(
                db,
                job.dataset_id
            )
        )

        if not dataset:

            raise ValueError(
                "Dataset not found"
            )

        return TrainingRuntime(

            training_job_id=
                job.id,

            dataset_id=
                dataset.id,

            provider_id=
                provider.id,

            provider_code=
                provider.code,

            provider_type=
                provider.provider_type,

            base_model=
                job.base_model,

            training_type=
                job.training_type,

            status=
                job.status,

            artifact_path=
                job.artifact_path
        )


training_runtime_service = (
    TrainingRuntimeService()
)