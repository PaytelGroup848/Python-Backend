import time

from fastapi import (
    HTTPException,
    status,
)

from app.modules.inference_runtime.schemas.inference_request import (
    InferenceRequest,
)

from app.modules.inference_runtime.schemas.inference_response import (
    InferenceResponse,
)


class InferenceService:

    async def generate(

        self,

        runtime,

        request: InferenceRequest,

    ) -> InferenceResponse:

        if runtime is None:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Model runtime is not available",

            )

        start_time = time.perf_counter()

        result = await runtime.generate(

            request=request,

        )

        latency_ms = (

            time.perf_counter()

            - start_time

        ) * 1000

        return InferenceResponse(

            text=result.text,

            finish_reason=result.finish_reason,

            prompt_tokens=result.prompt_tokens,

            generated_tokens=result.generated_tokens,

            total_tokens=result.total_tokens,

            latency_ms=latency_ms,

        )


inference_service = InferenceService()