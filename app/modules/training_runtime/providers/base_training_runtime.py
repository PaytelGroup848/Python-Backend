from abc import (
    ABC,
    abstractmethod,
)

from app.modules.training_runtime.contracts.training_data_stream import (
    TrainingDataStream,
)

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime,
)

from app.modules.training_runtime.schemas.training_result_schema import (
    TrainingResult,
)

from app.modules.training_runtime.schemas.training_execution_context import (
    TrainingExecutionContext,
)


class BaseTrainingRuntime(
    ABC
):

    @abstractmethod
    async def execute(
        self,
        runtime: TrainingRuntime,
        training_data: TrainingDataStream,
        context: TrainingExecutionContext,
    ) -> TrainingResult:
        """
        Execute a training job using a bounded
        asynchronous training-data stream and
        explicit execution context.
        """
        raise NotImplementedError