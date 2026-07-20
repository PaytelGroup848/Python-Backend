from abc import (
    ABC,
    abstractmethod,
)

from app.modules.evaluations.contracts.evaluation_data_stream import (
    EvaluationDataStream,
)

from app.modules.evaluations.schemas.evaluation_runtime_schema import (
    EvaluationRuntime,
)

from app.modules.evaluations.schemas.evaluation_result_schema import (
    EvaluationResult,
)

from app.modules.evaluations.schemas.evaluation_execution_context import (
    EvaluationExecutionContext,
)


class BaseEvaluationRuntime(
    ABC,
):

    @abstractmethod
    async def execute(
        self,
        runtime: EvaluationRuntime,
        evaluation_data: EvaluationDataStream,
        context: EvaluationExecutionContext,
    ) -> EvaluationResult:
        """
        Execute an evaluation job using a bounded
        asynchronous evaluation-data stream and
        explicit execution context.
        """
        raise NotImplementedError