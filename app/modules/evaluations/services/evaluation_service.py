from time import perf_counter

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.evaluations.models.evaluation_job import (
    EvaluationJob,
)

from app.modules.evaluations.repositories.evaluation_job_repository import (
    evaluation_job_repository,
)

from app.modules.evaluations.schemas.evaluation_job_create import (
    EvaluationJobCreate,
)

from app.modules.evaluations.schemas.evaluation_job_response import (
    EvaluationJobResponse,
)

from app.modules.evaluations.services.evaluation_executor_service import (
    evaluation_executor_service,
)

from app.modules.evaluations.schemas.evaluation_execution_context import (
    EvaluationExecutionContext,
)

from app.modules.evaluations.schemas.evaluation_runtime_schema import (
    EvaluationRuntime,
)


class EvaluationService:

    async def create_job(
        self,
        db: AsyncSession,
        request: EvaluationJobCreate,
    ) -> EvaluationJobResponse:

        job = EvaluationJob(
            artifact_id=request.artifact_id,
            dataset_version_id=request.dataset_version_id,
            evaluation_type=request.evaluation_type,
            runtime_configuration=request.runtime_configuration,
            status="pending",
        )

        await evaluation_job_repository.create(
            db=db,
            evaluation_job=job,
        )

        await db.commit()
        await db.refresh(job)

        return EvaluationJobResponse.model_validate(job)


    async def get_job(
        self,
        db: AsyncSession,
        evaluation_job_id: int,
    ) -> EvaluationJobResponse:

        job = await (
            evaluation_job_repository.get_by_id(
                db=db,
                evaluation_job_id=evaluation_job_id,
            )
        )

        if job is None:
            raise ValueError(
                "Evaluation job not found."
            )

        return EvaluationJobResponse.model_validate(job)


    async def execute_job(
        self,
        db: AsyncSession,
        evaluation_job_id: int,
    ) -> EvaluationJobResponse:

        job = await (
            evaluation_job_repository.get_by_id(
                db=db,
                evaluation_job_id=evaluation_job_id,
            )
        )

        if job is None:
            raise ValueError(
                "Evaluation job not found."
            )

        start = perf_counter()

        try:

            await evaluation_job_repository.mark_started(
                db=db,
                evaluation_job=job,
            )

            runtime = EvaluationRuntime(
                evaluation_job_id=job.id,
                artifact_id=job.artifact_id,
                dataset_version_id=job.dataset_version_id,
                evaluation_type=job.evaluation_type,
                runtime_configuration=(
                    job.runtime_configuration or {}
                ),
                runtime_class=(
                    job.runtime_configuration.get(
                        "runtime_class",
                        "app.modules.evaluations.providers.native_evaluation_runtime.NativeEvaluationRuntime",
                    )
                ),
            )

            context = EvaluationExecutionContext(
                db=db,
                evaluation_job_id=job.id,
                organization_id=getattr(
                    job,
                    "organization_id",
                    None,
                ),
                workspace_id=getattr(
                    job,
                    "workspace_id",
                    None,
                ),
            )

            result = await (
                evaluation_executor_service.execute(
                    runtime=runtime,
                    context=context,
                )
            )

            metrics = result.metrics

            summary = result.summary

            await evaluation_job_repository.save_metrics(
                db=db,
                evaluation_job=job,
                metrics=metrics,
                summary=summary,
            )

            duration_ms = (
                perf_counter() - start
            ) * 1000

            await evaluation_job_repository.mark_completed(
                db=db,
                evaluation_job=job,
                duration_ms=duration_ms,
            )

            await db.commit()

        except Exception as exc:

            await evaluation_job_repository.mark_failed(
                db=db,
                evaluation_job=job,
                reason=str(exc),
            )

            await db.commit()

            raise

        await db.refresh(job)

        return EvaluationJobResponse.model_validate(job)


evaluation_service = EvaluationService()