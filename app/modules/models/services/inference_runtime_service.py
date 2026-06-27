from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.models.schemas.inference_runtime_schema import (
    InferenceRuntime
)

from app.modules.models.repositories.model_deployment_repository import (
    model_deployment_repository
)


class InferenceRuntimeService:

    async def load_runtime(

        self,

        db: AsyncSession,

        model_version_id: int

    ) -> InferenceRuntime | None:

        deployment = await (
            model_deployment_repository
            .get_by_model_version(
                db=db,
                model_version_id=model_version_id
            )
        )

        if deployment is None:

            return None

        return InferenceRuntime(

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
                deployment.gpu_count
        )


inference_runtime_service = (
    InferenceRuntimeService()
)