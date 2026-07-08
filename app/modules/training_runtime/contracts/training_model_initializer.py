from abc import (
    ABC,
    abstractmethod,
)

from typing import (
    Any,
)

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime,
)


class TrainingModelInitializer(
    ABC
):

    @abstractmethod
    async def initialize(
        self,
        runtime: TrainingRuntime,
        configuration: dict,
    ) -> Any:
        """
        Construct and return a trainable model object
        from DB-resolved runtime configuration.
        """
        raise NotImplementedError