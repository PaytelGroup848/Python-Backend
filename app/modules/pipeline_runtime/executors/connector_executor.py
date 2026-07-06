from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.pipeline_runtime.executors.base_executor import (
    BaseExecutor,
)

from app.modules.pipeline_runtime.models.pipeline_run import (
    PipelineRun,
)

from app.modules.pipeline_runtime.models.pipeline_step_run import (
    PipelineStepRun,
)

from app.modules.data_pipelines.models.data_pipeline_step import (
    DataPipelineStep,
)

from app.modules.pipeline_runtime.schemas.executor_result import (
    ExecutorResult,
)

from app.modules.connector_registry.services.connector_execution_service import (
    connector_execution_service,
)


class ConnectorExecutor(
    BaseExecutor,
):

    async def execute(
        self,
        db: AsyncSession,
        pipeline_run: PipelineRun,
        pipeline_step_run: PipelineStepRun,
        pipeline_step: DataPipelineStep,
    ) -> ExecutorResult:

        configuration = (
            pipeline_step.configuration_json
            or
            {}
        )

        connector_instance_id = (
            configuration.get(
                "connector_instance_id"
            )
        )

        if connector_instance_id is None:

            raise ValueError(
                "connector_instance_id is required."
            )

        execution_result = await (
            connector_execution_service
            .execute(
                db=db,
                connector_instance_id=(
                    connector_instance_id
                ),
                configuration=configuration,
            )
        )

        return ExecutorResult(
            metrics={
                "connector_instance_id": (
                    execution_result[
                        "connector_instance_id"
                    ]
                ),
                "connector_implementation_id": (
                    execution_result[
                        "connector_implementation_id"
                    ]
                ),
                "implementation_code": (
                    execution_result[
                        "implementation_code"
                    ]
                ),
            },
            outputs=[],
        )


connector_executor = (
    ConnectorExecutor()
)