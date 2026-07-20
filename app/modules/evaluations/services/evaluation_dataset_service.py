from app.modules.evaluations.contracts.evaluation_data_stream import (
    EvaluationDataStream,
)


class EmptyEvaluationDataStream(
    EvaluationDataStream,
):

    async def stream(
        self,
    ):
        if False:
            yield


class EvaluationDatasetService:

    async def load(
        self,
        *,
        runtime,
        context,
    ) -> EvaluationDataStream:

        return EmptyEvaluationDataStream()


evaluation_dataset_service = (
    EvaluationDatasetService()
)