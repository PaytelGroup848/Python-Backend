from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.model_artifacts.models.model_artifact import (
    ModelArtifact
)


class ModelArtifactRepository:

    async def create(

        self,

        db: AsyncSession,

        artifact: ModelArtifact

    ):

        db.add(
            artifact
        )

        await db.flush()

        await db.refresh(
            artifact
        )

        return artifact

    async def get_by_id(

        self,

        db: AsyncSession,

        artifact_id: int

    ):

        result = await db.execute(

            select(
                ModelArtifact
            )
            .where(
                ModelArtifact.id
                ==
                artifact_id
            )
        )

        return result.scalar_one_or_none()

    async def list_by_training_job(

        self,

        db: AsyncSession,

        training_job_id: int

    ):

        result = await db.execute(

            select(
                ModelArtifact
            )
            .where(
                ModelArtifact.training_job_id
                ==
                training_job_id
            )
        )

        return result.scalars().all()


model_artifact_repository = (
    ModelArtifactRepository()
)