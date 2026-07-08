from abc import (
    ABC,
    abstractmethod,
)

from collections.abc import (
    AsyncIterator,
)

from app.modules.training_runtime.schemas.training_data_batch import (
    TrainingDataBatch,
)


class TrainingDataStream(
    ABC
):

    @abstractmethod
    def iter_batches(
        self,
    ) -> AsyncIterator[
        TrainingDataBatch
    ]:
        raise NotImplementedError