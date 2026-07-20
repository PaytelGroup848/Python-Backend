class EvaluationMetricService:

    async def evaluate(
        self,
        *,
        runtime,
        predictions,
        references,
    ) -> dict:

        metrics = {}

        return metrics


evaluation_metric_service = (
    EvaluationMetricService()
)