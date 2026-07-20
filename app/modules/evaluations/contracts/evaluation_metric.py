from abc import (
    ABC,
    abstractmethod,
)

from typing import (
    Any,
)


class EvaluationMetric(
    ABC,
):

    @abstractmethod
    async def evaluate(
        self,
        *,
        predictions: Any,
        references: Any,
    ) -> dict:
        raise NotImplementedError