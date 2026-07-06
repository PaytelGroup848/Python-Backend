from abc import (
    ABC,
    abstractmethod,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
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


class BaseExecutor(
    ABC,
):

    @abstractmethod
    async def execute(
        self,
        db: AsyncSession,
        pipeline_run: PipelineRun,
        pipeline_step_run: PipelineStepRun,
        pipeline_step: DataPipelineStep,
    ) -> ExecutorResult:

        raise NotImplementedError