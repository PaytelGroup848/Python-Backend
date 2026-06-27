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

            .order_by(
                ModelArtifact.created_at.desc()
            )
        )

        return result.scalars().all()
    
    async def get_by_type(

        self,

        db: AsyncSession,

        training_job_id: int,

        artifact_type: str

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

            .where(
                ModelArtifact.artifact_type
                == 
                artifact_type
            )

            .order_by(
                ModelArtifact.created_at.desc()
            )

        )

        return result.scalars().all()
    
    async def get_latest(

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

            .order_by(
                ModelArtifact.created_at.desc()
            )

            .limit(1)

        )

        return result.scalar_one_or_none()
    
    async def delete(

        self,

        db: AsyncSession,

        artifact: ModelArtifact

    ):

        await db.delete(
            artifact
        )

    async def update(

        self,

        db: AsyncSession,

        artifact: ModelArtifact

    ):

        await db.flush()

        await db.refresh(
            artifact
        )

        return artifact


model_artifact_repository = (
    ModelArtifactRepository()
)