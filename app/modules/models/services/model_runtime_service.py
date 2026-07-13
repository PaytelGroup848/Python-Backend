from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.models.schemas.model_runtime_schema import (
    ModelRuntime
)

from app.modules.models.repositories.model_version_repository import (
    model_version_repository
)

from app.modules.models.repositories.model_deployment_repository import (
    model_deployment_repository,
)


class ModelRuntimeService:

    async def load_runtime(

        self,

        db: AsyncSession,

        assistant_id: int

    ) -> ModelRuntime | None:

        runtime = await (
            model_version_repository
            .get_runtime_by_assistant(
                db=db,
                assistant_id=assistant_id
            )
        )

        if runtime is None:
            return None

        mapping, version, model = runtime

        deployment = await (
            model_deployment_repository
            .get_by_model_version(
                db=db,
                model_version_id=version.id,
            )
        )

        if deployment is None:

            raise ValueError(
                "No active deployment found "
                "for model version."
            )

        return ModelRuntime(

            model_id=
                model.id,

            model_version_id=
                version.id,

            provider_id=
                model.provider_id,

            model_code=
                model.code,

            model_display_name=
                model.display_name,

            version=
                version.version,

            version_display_name=
                version.display_name,

            deployment_id=
                deployment.id,

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

            deployment_active=
                deployment.is_active,

            is_default=
                mapping.is_default,
        )


model_runtime_service = (
    ModelRuntimeService()
)