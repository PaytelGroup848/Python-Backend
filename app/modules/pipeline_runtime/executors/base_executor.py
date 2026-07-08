from abc import (
    ABC,
    abstractmethod,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.pipeline_runtime.schemas.executor_result import (
    ExecutorResult,
)

from app.modules.pipeline_runtime.schemas.pipeline_execution_context import (
    PipelineExecutionContext,
)


class BaseExecutor(
    ABC,
):

    @abstractmethod
    async def execute(
        self,
        db: AsyncSession,
        context: PipelineExecutionContext,
    ) -> ExecutorResult:

        raise NotImplementedError