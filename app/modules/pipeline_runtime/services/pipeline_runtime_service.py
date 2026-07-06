from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.data_pipelines.repositories.data_pipeline_repository import (
    data_pipeline_repository
)

from app.modules.data_pipelines.repositories.data_pipeline_step_repository import (
    data_pipeline_step_repository
)

from app.modules.pipeline_runtime.registry.executor_registry import (
    executor_registry
)

from app.modules.pipeline_runtime.services.pipeline_run_service import (
    pipeline_run_service
)

from app.modules.pipeline_runtime.services.pipeline_step_runtime_service import (
    pipeline_step_runtime_service
)

from app.modules.pipeline_runtime.schemas.pipeline_run_create import (
    PipelineRunCreate
)

from app.modules.pipeline_runtime.schemas.pipeline_step_run_create import (
    PipelineStepRunCreate
)

from app.shared.enums.execution_status import (
    ExecutionStatus
)

from app.shared.enums.trigger_type import (
    TriggerType
)

from app.shared.exceptions.business_exception import (
    BusinessException
)

from app.shared.utils.code_generator import (
    generate_pipeline_run_code,
    generate_pipeline_step_run_code
)


class PipelineRuntimeService:

    async def execute_pipeline(
        self,
        db: AsyncSession,
        pipeline_id: int,
        dataset_id: int | None = None,
        corpus_source_id: int | None = None,
        trigger_type: TriggerType = TriggerType.API
    ):

        pipeline = await (
            data_pipeline_repository
            .get_by_id(
                db,
                pipeline_id
            )
        )

        if not pipeline:

            raise BusinessException(
                "Pipeline not found."
            )

        steps = await (
            data_pipeline_step_repository
            .list_by_pipeline(
                db,
                pipeline_id
            )
        )

        if not steps:

            raise BusinessException(
                "Pipeline contains no steps."
            )

        pipeline_run = await (
            pipeline_run_service
            .create_run(
                db,
                PipelineRunCreate(

                    pipeline_id=pipeline.id,

                    dataset_id=dataset_id,

                    corpus_source_id=corpus_source_id,

                    run_code=generate_pipeline_run_code(),

                    trigger_type=trigger_type.value,

                    status=ExecutionStatus.PENDING.value
                )
            )
        )

        await (
            pipeline_run_service
            .start(
                db,
                pipeline_run
            )
        )

        metrics = []

        try:

            for step in steps:

                step_run = await (
                    pipeline_step_runtime_service
                    .create_step_run(
                        db,
                        PipelineStepRunCreate(

                            pipeline_run_id=pipeline_run.id,

                            pipeline_step_id=step.id,

                            step_run_code=generate_pipeline_step_run_code(),

                            execution_order=step.step_order,

                            status=ExecutionStatus.PENDING.value
                        )
                    )
                )

                await (
                    pipeline_step_runtime_service
                    .start(
                        db,
                        step_run
                    )
                )

                executor = executor_registry.get_executor(
                    step.step_type
                )

                executor_result = await (
                    executor.execute(
                        db=db,
                        pipeline_run=pipeline_run,
                        pipeline_step_run=step_run,
                        pipeline_step=step,
                    )
                )

                await (
                    pipeline_step_runtime_service
                    .complete(
                        db,
                        step_run,
                        executor_result.metrics,
                    )
                )

                metrics.append(
                    executor_result.metrics
                )

            await (
                pipeline_run_service
                .complete(
                    db,
                    pipeline_run,
                    {
                        "steps": metrics
                    }
                )
            )

            return pipeline_run

        except Exception as ex:

            await (
                pipeline_run_service
                .fail(
                    db,
                    pipeline_run,
                    str(ex)
                )
            )

            raise


pipeline_runtime_service = (
    PipelineRuntimeService()
)