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

class TrainingExecutorService:

    async def execute(

        self,

        db: AsyncSession,

        training_job_id: int

    ) -> TrainingResult:

        runtime = await (
            training_runtime_service
            .load_runtime(
                db,
                training_job_id
            )
        )

        if not runtime.provider_code:

            raise ValueError(
                "Training provider missing"
            )

        job = await (
            training_job_repository
            .get_by_id(
                db,
                training_job_id
            )
        )

        await (
            training_status_service
            .update_status(
                db,
                job,
                "running"
            )
        )

        if runtime.provider_code == "local_gpu":

            artifact_path = (
                f"/artifacts/local/{training_job_id}"
            )

        elif runtime.provider_code == "runpod":

            artifact_path = (
                f"/artifacts/runpod/{training_job_id}"
            )

        elif runtime.provider_code == "aws_sagemaker":

            artifact_path = (
                f"/artifacts/aws/{training_job_id}"
            )

        elif runtime.provider_code == "kubernetes_gpu":

            artifact_path = (
                f"/artifacts/k8s/{training_job_id}"
            )

        else:

            raise ValueError(
                f"Unsupported provider: "
                f"{runtime.provider_code}"
            )

        job.artifact_path = artifact_path

        await (
            training_job_repository
            .update(
                db,
                job
            )
        )

        await (
            training_status_service
            .update_status(
                db,
                job,
                "completed"
            )
        )

        await db.commit()

        return TrainingResult(

            success=True,

            training_job_id=
                training_job_id,

            artifact_path=
                artifact_path,

            message=
                "Training completed"
        )


training_executor_service = (
    TrainingExecutorService()
)