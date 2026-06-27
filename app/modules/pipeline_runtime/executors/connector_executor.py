from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.pipeline_runtime.executors.base_executor import (
    BaseExecutor
)

from app.modules.pipeline_runtime.models.pipeline_run import (
    PipelineRun
)

from app.modules.pipeline_runtime.models.pipeline_step_run import (
    PipelineStepRun
)

from app.modules.data_pipelines.models.data_pipeline_step import (
    DataPipelineStep
)

from app.modules.connector_registry.services.connector_execution_service import (
    connector_execution_service
)


class ConnectorExecutor(
    BaseExecutor
):

    async def execute(
        self,
        db: AsyncSession,
        pipeline_run: PipelineRun,
        pipeline_step_run: PipelineStepRun,
        pipeline_step: DataPipelineStep
    ) -> dict:

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

        metrics = await (
            connector_execution_service
            .execute(
                db=db,
                connector_instance_id=connector_instance_id,
                configuration=configuration
            )
        )

        return metrics


connector_executor = (
    ConnectorExecutor()
)