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

    @property
    @abstractmethod
    def dataset_snapshot_id(
        self,
    ) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def resume_after_record_id(
        self,
    ) -> int | None:
        raise NotImplementedError

    @abstractmethod
    def iter_batches(
        self,
    ) -> AsyncIterator[
        TrainingDataBatch
    ]:
        raise NotImplementedError

    @abstractmethod
    def request_cancel(
        self,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def aclose(
        self,
    ) -> None:
        raise NotImplementedError