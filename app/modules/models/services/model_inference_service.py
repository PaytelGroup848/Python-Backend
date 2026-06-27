from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.models.services.inference_runtime_service import (
    inference_runtime_service
)

from app.modules.models.schemas.model_generation_request import (
    ModelGenerationRequest
)

from app.modules.models.schemas.model_generation_response import (
    ModelGenerationResponse
)


class ModelInferenceService:

    async def generate(

        self,

        db: AsyncSession,

        model_version_id: int,

        request: ModelGenerationRequest

    ) -> ModelGenerationResponse:

        inference_runtime = await (
            inference_runtime_service
            .load_runtime(
                db=db,
                model_version_id=model_version_id
            )
        )

        if inference_runtime is None:

            raise RuntimeError(
                "Active deployment not found."
            )

        #
        # vLLM / TGI call will come later
        #

        return ModelGenerationResponse(

            text=
                "Inference runtime not implemented.",

            model_version_id=
                model_version_id,

            deployment_name=
                inference_runtime.deployment_name
        )


model_inference_service = (
    ModelInferenceService()
)