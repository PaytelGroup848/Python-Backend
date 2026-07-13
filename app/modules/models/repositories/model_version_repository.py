from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant_model_version import (
    AssistantModelVersion
)

from app.models.model_version import (
    ModelVersion
)

from app.models.model import (
    ModelRegistry
)


class ModelVersionRepository:

    async def get_runtime_by_assistant(
        self,
        db: AsyncSession,
        assistant_id: int
    ):

        stmt = (

            select(

                AssistantModelVersion,

                ModelVersion,

                ModelRegistry

            )

            .join(

                ModelVersion,

                AssistantModelVersion
                .model_version_id
                ==
                ModelVersion.id
            )

            .join(

                ModelRegistry,

                ModelVersion.model_id
                ==
                ModelRegistry.id
            )

            .where(

                AssistantModelVersion
                .assistant_id
                ==
                assistant_id,

                AssistantModelVersion
                .is_active
                ==
                True,

                AssistantModelVersion
                .is_default
                ==
                True
            )
        )

        result = await db.execute(
            stmt
        )

        return result.first()
    async def create(
        self,
        db: AsyncSession,
        model_version: ModelVersion,
    ):

        db.add(model_version)

        await db.flush()

        await db.refresh(
            model_version
        )

        return model_version
    
    async def update(
        self,
        db: AsyncSession,
        model_version: ModelVersion,
    ):

        await db.flush()

        await db.refresh(
            model_version
        )

        return model_version
    
    async def get_by_id(
        self,
        db: AsyncSession,
        model_version_id: int,
    ):

        result = await db.execute(
 
            select(
                ModelVersion
            ).where(
                ModelVersion.id
                ==
                model_version_id
            )
        )

        return result.scalar_one_or_none()
    
    async def list_by_model(
        self,
        db: AsyncSession,
        model_id: int,
    ):

        result = await db.execute(
 
            select(
                ModelVersion
            )

            .where(
                ModelVersion.model_id
                ==
                model_id
            )

            .order_by(
                ModelVersion.created_at.desc()
            )
        )

        return result.scalars().all()
    
    async def get_latest_version(
        self,
        db: AsyncSession,
        model_id: int,
    ):

        result = await db.execute(

            select(
                ModelVersion
            )

            .where(
                ModelVersion.model_id
                ==
                model_id
            )

            .order_by(
                ModelVersion.created_at.desc()
            )

            .limit(1)
        )

        return result.scalar_one_or_none()
    
    async def get_by_training_job(
        self,
        db: AsyncSession,
        training_job_id: int,
    ):

        result = await db.execute(

            select(
                ModelVersion
            )

            .where(
                ModelVersion.training_job_id
                ==
                training_job_id
            )
        )

        return result.scalar_one_or_none()
    
    async def get_by_artifact(
        self,
        db: AsyncSession,
        artifact_id: int,
    ):

        result = await db.execute(
 
            select(
                ModelVersion
            )

            .where(
                ModelVersion.artifact_id
                ==
                artifact_id
            )
        )

        return result.scalar_one_or_none()
    
    async def get_inference_runtime(
        self,
        db: AsyncSession,
        model_version_id: int,
    ):
       ...
    
    async def list_by_status(
        self,
        db: AsyncSession,
        status: str,
    ):

        result = await db.execute(

            select(
                ModelVersion
            )

            .where(
                ModelVersion.status
                ==
                status
            )

            .order_by(
                ModelVersion.created_at.desc()
            )
        )

        return result.scalars().all()
    
    async def delete(
        self,
        db: AsyncSession,
        model_version: ModelVersion,
    ):

        await db.delete(
            model_version
        )


model_version_repository = (
    ModelVersionRepository()
)