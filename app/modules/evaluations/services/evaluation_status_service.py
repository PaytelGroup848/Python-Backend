class EvaluationStatusService:

    async def started(
        self,
        *,
        runtime,
        context,
    ):

        return

    async def completed(
        self,
        *,
        runtime,
        context,
    ):

        return

    async def failed(
        self,
        *,
        runtime,
        context,
        reason: str,
    ):

        return


evaluation_status_service = (
    EvaluationStatusService()
)