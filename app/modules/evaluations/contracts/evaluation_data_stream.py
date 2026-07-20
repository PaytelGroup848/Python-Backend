from abc import (
    ABC,
    abstractmethod,
)

from collections.abc import (
    AsyncIterator,
)

from app.modules.evaluations.schemas.evaluation_data_record import (
    EvaluationDataRecord,
)


class EvaluationDataStream(
    ABC,
):

    @abstractmethod
    async def stream(
        self,
    ) -> AsyncIterator[
        EvaluationDataRecord
    ]:
        raise NotImplementedError