from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.training_runtime.services.training_runtime_service import (
    training_runtime_service
)

from app.modules.training_runtime.services.training_status_service import (
    training_status_service
)

from app.modules.training_runtime.schemas.training_result_schema import (
    TrainingResult
)

from app.modules.training.repositories.training_job_repository import (
    training_job_repository
)

from app.modules.training_runtime.providers.runtime_factory import (
    training_runtime_factory
)
from app.shared.constants.training_status import (
    TrainingStatus
)

class TrainingExecutorService:

    async def execute(

        self,

        db: AsyncSession,

        training_job_id: int

    ) -> TrainingResult:

        runtime = await (
            training_runtime_service
            .load_runtime(
                db=db,
                training_job_id=training_job_id
            )
        )

        if not runtime.provider_code:

            raise ValueError(
                "Training provider missing"
            )

        job = await (
            training_job_repository
            .get_by_id(
                db=db,
                training_job_id=training_job_id
            )
        )

        await (
            training_status_service
            .update_status(
                db=db,
                training_job=job,
                status=TrainingStatus.RUNNING
            )
        )

        runtime_provider = (
            training_runtime_factory
            .get_runtime(
                runtime.runtime_code
            )
        )

        result = await (
            runtime_provider.execute(
                runtime=runtime
            )
        )

        job.artifact_path = (
            result.artifact_directory
        )

        

        await (
            training_job_repository
            .update(
                db=db,
                training_job=job
            )
        )

        await (
            training_status_service
            .update_status(
                db,
                job,
                TrainingStatus.COMPLETED
            )
        )

        await db.commit()

        return result


training_executor_service = (
    TrainingExecutorService()
)