import time

from fastapi import (
    HTTPException,
    status
)

from app.modules.inference_runtime.schemas.inference_request import (
    InferenceRequest
)

from app.modules.inference_runtime.schemas.inference_response import (
    InferenceResponse
)

from app.modules.model_runtime.schemas.loaded_model import (
    LoadedModel
)


class InferenceManager:

    async def generate(

        self,

        runtime: LoadedModel,

        request: InferenceRequest

    ) -> InferenceResponse:

        if runtime is None:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Model runtime is not available"

            )

        start_time = time.perf_counter()

        #
        # Execute Inference
        #
        # runtime internally knows whether it is
        # llama.cpp
        # transformers
        # vLLM
        # TensorRT
        #
        try:

            result = await runtime.generate(

                request=request

            )

        except Exception as exc:

            raise HTTPException(

                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

                detail=f"Inference failed: {str(exc)}"

            )

        latency_ms = int(

            (

                time.perf_counter()

                - start_time

            ) * 1000

        )

        return InferenceResponse(

            text=result.text,

            finish_reason=result.finish_reason,

            prompt_tokens=result.prompt_tokens,

            generated_tokens=result.generated_tokens,

            total_tokens=result.total_tokens,

            latency_ms=latency_ms

        )


inference_manager = (
    InferenceManager()
)