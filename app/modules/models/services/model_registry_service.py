from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.models.repositories.model_version_repository import (
    model_version_repository
)


class ModelRegistryService:

    async def get_active_model_version(

        self,

        db: AsyncSession,

        assistant_id: int

    ):

        return await (
            model_version_repository
            .get_runtime_by_assistant(
                db=db,
                assistant_id=assistant_id
            )
        )


model_registry_service = (
    ModelRegistryService()
)