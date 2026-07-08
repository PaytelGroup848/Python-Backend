from abc import (
    ABC,
    abstractmethod,
)

from typing import (
    Any,
)

from app.modules.training_runtime.contracts.trainable_model import (
    TrainableModel,
)

from app.modules.training_runtime.schemas.tokenized_training_sample import (
    TokenizedTrainingSample,
)

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime,
)


class TrainingStrategy(
    ABC
):

    @abstractmethod
    async def initialize(
        self,
        runtime: TrainingRuntime,
        model: TrainableModel,
        configuration: dict,
    ) -> Any:
        """
        Initialize strategy-specific runtime state.

        Examples may include optimizer state,
        scheduler state, loss state, precision state,
        or distributed execution state.

        Concrete behavior is supplied by the
        dynamically configured strategy class.
        """
        raise NotImplementedError

    @abstractmethod
    async def train_batch(
        self,
        runtime: TrainingRuntime,
        model: TrainableModel,
        strategy_state: Any,
        samples: list[
            TokenizedTrainingSample
        ],
        configuration: dict,
    ) -> dict:
        """
        Execute one training batch and return
        strategy-defined metrics.
        """
        raise NotImplementedError

    @abstractmethod
    async def finalize(
        self,
        runtime: TrainingRuntime,
        model: TrainableModel,
        strategy_state: Any,
        configuration: dict,
    ) -> dict:
        """
        Finalize strategy execution and return
        strategy-defined metadata.
        """
        raise NotImplementedError