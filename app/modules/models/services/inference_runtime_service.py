from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.models.schemas.inference_runtime_schema import (
    InferenceRuntime
)

from app.modules.models.repositories.model_version_repository import (
    model_version_repository,
)


class InferenceRuntimeService:

    async def load_runtime(

        self,

        db: AsyncSession,

        model_version_id: int

    ) -> InferenceRuntime | None:

        runtime = await (
            model_version_repository
            .get_inference_runtime(
                db=db,
                model_version_id=model_version_id,
            )
        )

        if runtime is None:

            return None
        
        version, model, deployment = runtime

        return InferenceRuntime(

            model_id=
                model.id,

            provider_id=
                model.provider_id,

            model_code=
                model.code,

            model_display_name=
                model.display_name,

            model_version=
                version.version,

            deployment_id=
                deployment.id,

            model_version_id=
                deployment.model_version_id,

            deployment_name=
                deployment.deployment_name,

            deployment_type=
                deployment.deployment_type,

            endpoint_url=
                deployment.endpoint_url,

            max_context_window=
                deployment.max_context_window,

            gpu_type=
                deployment.gpu_type,

            gpu_count=
                deployment.gpu_count,
        )


inference_runtime_service = (
    InferenceRuntimeService()
)