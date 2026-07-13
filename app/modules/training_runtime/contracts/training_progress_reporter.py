from abc import (
    ABC,
    abstractmethod,
)

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime,
)
from app.modules.training_runtime.schemas.training_execution_context import (
    TrainingExecutionContext,
)

class TrainingProgressReporter(
    ABC
):

    @abstractmethod
    async def on_training_started(
        self,
        runtime: TrainingRuntime,
        context: TrainingExecutionContext,
    ) -> None:
        ...

    @abstractmethod
    async def on_epoch_started(
        self,
        runtime: TrainingRuntime,
        context: TrainingExecutionContext,
        epoch: int,
    ) -> None:
        ...

    @abstractmethod
    async def on_batch_completed(
        self,
        runtime: TrainingRuntime,
        context: TrainingExecutionContext,
        epoch: int,
        step: int,
        global_step: int,
        current_loss: float | None,
        learning_rate: float | None,
        processed_samples: int,
        processed_tokens: int,
    ) -> None:
        ...

    @abstractmethod
    async def on_checkpoint_saved(
        self,
        runtime: TrainingRuntime,
        context: TrainingExecutionContext,
        checkpoint_path: str,
    ) -> None:
        ...

    @abstractmethod
    async def on_training_completed(
        self,
        runtime: TrainingRuntime,
        context: TrainingExecutionContext,
    ) -> None:
        ...

    @abstractmethod
    async def on_training_failed(
        self,
        runtime: TrainingRuntime,
        context: TrainingExecutionContext,
        failure_reason: str,
    ) -> None:
        ...