from datetime import datetime

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.pipeline_runtime.models.pipeline_run import (
    PipelineRun
)

from app.modules.pipeline_runtime.schemas.pipeline_run_create import (
    PipelineRunCreate
)

from app.modules.pipeline_runtime.repositories.pipeline_run_repository import (
    pipeline_run_repository
)

from app.shared.enums.execution_status import (
    ExecutionStatus
)

from app.shared.exceptions.business_exception import (
    BusinessException
)


class PipelineRunService:

    async def create_run(
        self,
        db: AsyncSession,
        payload: PipelineRunCreate
    ):

        existing = await (
            pipeline_run_repository
            .get_by_run_code(
                db,
                payload.run_code
            )
        )

        if existing:

            raise BusinessException(
                "Pipeline run code already exists."
            )

        pipeline_run = PipelineRun(

            pipeline_id=payload.pipeline_id,

            dataset_id=payload.dataset_id,

            corpus_source_id=payload.corpus_source_id,

            run_code=payload.run_code,

            trigger_type=payload.trigger_type,

            status=payload.status,

            metrics_json=payload.metrics_json,

            error_message=payload.error_message
        )

        return await (
            pipeline_run_repository
            .create(
                db,
                pipeline_run
            )
        )

    async def get_by_id(
        self,
        db: AsyncSession,
        pipeline_run_id: int
    ):

        return await (
            pipeline_run_repository
            .get_by_id(
                db,
                pipeline_run_id
            )
        )

    async def get_by_code(
        self,
        db: AsyncSession,
        run_code: str
    ):

        return await (
            pipeline_run_repository
            .get_by_run_code(
                db,
                run_code
            )
        )

    async def list_by_pipeline(
        self,
        db: AsyncSession,
        pipeline_id: int
    ):

        return await (
            pipeline_run_repository
            .list_by_pipeline(
                db,
                pipeline_id
            )
        )

    async def start(
        self,
        db: AsyncSession,
        pipeline_run: PipelineRun
    ):

        pipeline_run.status = (
            ExecutionStatus.RUNNING.value
        )

        pipeline_run.started_at = (
            datetime.utcnow()
        )

        return await (
            pipeline_run_repository
            .update(
                db,
                pipeline_run
            )
        )

    async def complete(
        self,
        db: AsyncSession,
        pipeline_run: PipelineRun,
        metrics_json: dict | None = None
    ):

        pipeline_run.status = (
            ExecutionStatus.COMPLETED.value
        )

        pipeline_run.completed_at = (
            datetime.utcnow()
        )

        if metrics_json is not None:

            pipeline_run.metrics_json = (
                metrics_json
            )

        return await (
            pipeline_run_repository
            .update(
                db,
                pipeline_run
            )
        )

    async def fail(
        self,
        db: AsyncSession,
        pipeline_run: PipelineRun,
        error_message: str
    ):

        pipeline_run.status = (
            ExecutionStatus.FAILED.value
        )

        pipeline_run.completed_at = (
            datetime.utcnow()
        )

        pipeline_run.error_message = (
            error_message
        )

        return await (
            pipeline_run_repository
            .update(
                db,
                pipeline_run
            )
        )


pipeline_run_service = (
    PipelineRunService()
)