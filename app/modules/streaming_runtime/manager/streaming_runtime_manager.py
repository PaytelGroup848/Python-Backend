from app.modules.inference_runtime.schemas.inference_request import (
    InferenceRequest
)

from app.modules.streaming_runtime.services.streaming_runtime_service import (
    streaming_runtime_service
)


class StreamingRuntimeManager:

    async def stream(

        self,

        runtime,

        request: InferenceRequest

    ):

        async for token in (

            streaming_runtime_service.stream(

                runtime=runtime,

                request=request

            )

        ):

            yield token


streaming_runtime_manager = (
    StreamingRuntimeManager()
)