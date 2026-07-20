from abc import (
    ABC,
    abstractmethod,
)

from app.modules.evaluations.contracts.evaluation_result import (
    EvaluationResult,
)


class EvaluationRuntime(
    ABC,
):

    @abstractmethod
    async def execute(
        self,
    ) -> EvaluationResult:
        """
        Execute a complete evaluation run and
        return the evaluation result.
        """
        raise NotImplementedError