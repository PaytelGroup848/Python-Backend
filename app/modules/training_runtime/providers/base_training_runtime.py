from abc import ABC, abstractmethod

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime
)

from app.modules.training_runtime.schemas.training_result_schema import (
    TrainingResult
)


class BaseTrainingRuntime(ABC):

    @abstractmethod
    async def execute(
        self,
        runtime: TrainingRuntime
    ) -> TrainingResult:
        """
        Execute a training job.
        """
        raise NotImplementedError