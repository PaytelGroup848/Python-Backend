from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.models.schemas.model_runtime_schema import (
    ModelRuntime
)

from app.modules.models.repositories.model_version_repository import (
    model_version_repository
)


class ModelRuntimeService:

    async def load_runtime(

        self,

        db: AsyncSession,

        assistant_id: int

    ) -> ModelRuntime | None:

        result = await (
            model_version_repository
            .get_runtime_by_assistant(
                db=db,
                assistant_id=assistant_id
            )
        )

        if not result:

            return None

        mapping, version, model = result

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

            is_default=
                mapping.is_default
        )


model_runtime_service = (
    ModelRuntimeService()
)