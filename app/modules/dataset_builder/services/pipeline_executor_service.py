from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dataset_builder.schemas.dataset_build_runtime import (
    DatasetBuildRuntime,
)

from app.modules.data_pipelines.repositories.data_pipeline_step_repository import (
    data_pipeline_step_repository,
)


class PipelineExecutorService:

    async def execute(
        self,
        db: AsyncSession,
        runtime: DatasetBuildRuntime,
    ):

        pipeline_steps = await (
            data_pipeline_step_repository
            .list_by_pipeline(
                db=db,
                pipeline_id=runtime.pipeline_id,
            )
        )

        if not pipeline_steps:

            raise ValueError(
                "Pipeline has no configured steps."
            )

        #
        # Step execution will be implemented next.
        #

        return None


pipeline_executor_service = (
    PipelineExecutorService()
)