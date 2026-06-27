from datetime import datetime

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.pipeline_runtime.models.pipeline_step_run import (
    PipelineStepRun
)

from app.modules.pipeline_runtime.schemas.pipeline_step_run_create import (
    PipelineStepRunCreate
)

from app.modules.pipeline_runtime.repositories.pipeline_step_run_repository import (
    pipeline_step_run_repository
)

from app.shared.enums.execution_status import (
    ExecutionStatus
)

from app.shared.exceptions.business_exception import (
    BusinessException
)


class PipelineStepRuntimeService:

    async def create_step_run(
        self,
        db: AsyncSession,
        payload: PipelineStepRunCreate
    ):

        existing = await (
            pipeline_step_run_repository
            .get_by_pipeline_run_and_step(
                db,
                payload.pipeline_run_id,
                payload.pipeline_step_id
            )
        )

        if existing:

            raise BusinessException(
                "Pipeline step run already exists."
            )

        pipeline_step_run = PipelineStepRun(

            pipeline_run_id=payload.pipeline_run_id,

            pipeline_step_id=payload.pipeline_step_id,

            step_run_code=payload.step_run_code,

            execution_order=payload.execution_order,

            status=payload.status,

            metrics_json=payload.metrics_json,

            error_message=payload.error_message
        )

        return await (
            pipeline_step_run_repository
            .create(
                db,
                pipeline_step_run
            )
        )

    async def get_by_id(
        self,
        db: AsyncSession,
        pipeline_step_run_id: int
    ):

        return await (
            pipeline_step_run_repository
            .get_by_id(
                db,
                pipeline_step_run_id
            )
        )

    async def get_by_code(
        self,
        db: AsyncSession,
        step_run_code: str
    ):

        return await (
            pipeline_step_run_repository
            .get_by_step_run_code(
                db,
                step_run_code
            )
        )

    async def list_by_pipeline_run(
        self,
        db: AsyncSession,
        pipeline_run_id: int
    ):

        return await (
            pipeline_step_run_repository
            .list_by_pipeline_run(
                db,
                pipeline_run_id
            )
        )

    async def start(
        self,
        db: AsyncSession,
        pipeline_step_run: PipelineStepRun
    ):

        pipeline_step_run.status = (
            ExecutionStatus.RUNNING.value
        )

        pipeline_step_run.started_at = (
            datetime.utcnow()
        )

        return await (
            pipeline_step_run_repository
            .update(
                db,
                pipeline_step_run
            )
        )

    async def complete(
        self,
        db: AsyncSession,
        pipeline_step_run: PipelineStepRun,
        metrics_json: dict | None = None
    ):

        pipeline_step_run.status = (
            ExecutionStatus.COMPLETED.value
        )

        pipeline_step_run.completed_at = (
            datetime.utcnow()
        )

        if metrics_json is not None:

            pipeline_step_run.metrics_json = (
                metrics_json
            )

        return await (
            pipeline_step_run_repository
            .update(
                db,
                pipeline_step_run
            )
        )

    async def fail(
        self,
        db: AsyncSession,
        pipeline_step_run: PipelineStepRun,
        error_message: str
    ):

        pipeline_step_run.status = (
            ExecutionStatus.FAILED.value
        )

        pipeline_step_run.completed_at = (
            datetime.utcnow()
        )

        pipeline_step_run.error_message = (
            error_message
        )

        return await (
            pipeline_step_run_repository
            .update(
                db,
                pipeline_step_run
            )
        )


pipeline_step_runtime_service = (
    PipelineStepRuntimeService()
)