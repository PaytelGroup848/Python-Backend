class EvaluationReportService:

    async def generate(
        self,
        *,
        runtime,
        metrics,
    ) -> dict:

        return {
            "metrics": metrics,
        }


evaluation_report_service = (
    EvaluationReportService()
)