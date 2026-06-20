from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.model_artifacts.models.model_artifact import (
    ModelArtifact
)

from app.modules.model_artifacts.repositories.model_artifact_repository import (
    model_artifact_repository
)

from app.modules.model_artifacts.schemas.model_artifact_create import (
    ModelArtifactCreate
)


class ModelArtifactService:

    async def create_artifact(

        self,

        db: AsyncSession,

        data: ModelArtifactCreate

    ):

        artifact = ModelArtifact(
            **data.model_dump()
        )

        return await (
            model_artifact_repository
            .create(
                db,
                artifact
            )
        )

    async def get_artifact(

        self,

        db: AsyncSession,

        artifact_id: int

    ):

        return await (
            model_artifact_repository
            .get_by_id(
                db,
                artifact_id
            )
        )


model_artifact_service = (
    ModelArtifactService()
)