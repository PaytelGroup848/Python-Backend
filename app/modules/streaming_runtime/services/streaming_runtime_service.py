from app.modules.inference_runtime.manager.inference_manager import (
    inference_manager
)

from app.modules.inference_runtime.schemas.inference_request import (
    InferenceRequest
)


class StreamingRuntimeService:

    async def stream(

        self,

        runtime,

        request: InferenceRequest

    ):

        async for token in (

            inference_manager.generate_stream(

                runtime=runtime,

                request=request

            )

        ):

            yield token


streaming_runtime_service = (
    StreamingRuntimeService()
)