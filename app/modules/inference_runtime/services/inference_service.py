from app.modules.model_runtime.schemas.loaded_model import (
    LoadedModel,
)

from app.modules.inference_runtime.manager.inference_manager import (
    inference_manager,
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

        runtime: LoadedModel,

        request: InferenceRequest,

    ) -> InferenceResponse:

        return await (

            inference_manager.generate(

                runtime=runtime,

                request=request,

            )

        )


inference_service = InferenceService()