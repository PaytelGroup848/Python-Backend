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

        artifact = await (
            model_artifact_repository
            .create(
                db=db,
                artifact=artifact
            )
        )

        return artifact

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
    
    async def list_training_artifacts(

        self,

        db: AsyncSession,

        training_job_id: int

    ):

        return await (
            model_artifact_repository
            .list_by_training_job(
                db=db,
                training_job_id=training_job_id
            )
        )
    
    async def get_latest_artifact(

        self,

        db: AsyncSession,

        training_job_id: int

    ):

        return await (
            model_artifact_repository
            .get_latest(
                db=db,
                training_job_id=training_job_id
            )
        )
    
    async def get_artifacts_by_type(

        self,

        db: AsyncSession,

        training_job_id: int,

        artifact_type: str

    ):

        return await (
            model_artifact_repository
            .get_by_type(
                db=db,
                training_job_id=training_job_id,
                artifact_type=artifact_type
            )
        )
    
    async def delete_artifact(

        self,

        db: AsyncSession,

        artifact_id: int

    ) -> bool:

        artifact = await (
            model_artifact_repository
            .get_by_id(
                db=db,
                artifact_id=artifact_id
            )
        )

        if artifact is None:

            return False

        await (
            model_artifact_repository
            .delete(
                db=db,
                artifact=artifact
            )
        )

        return True
    
    async def update_artifact(

        self,

        db: AsyncSession,

        artifact: ModelArtifact

    ):

        return await (
            model_artifact_repository
            .update(
                db=db,
                artifact=artifact
            )
        )


model_artifact_service = (
    ModelArtifactService()
)