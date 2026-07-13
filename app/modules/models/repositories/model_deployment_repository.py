from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.models.models.model_deployment import (
    ModelDeployment
)


class ModelDeploymentRepository:

    async def get_by_model_version(

        self,

        db: AsyncSession,

        model_version_id: int

    ):

        result = await db.execute(

            select(
                ModelDeployment
            )
            .where(
                ModelDeployment.model_version_id
                ==
                model_version_id,

                ModelDeployment.is_active
                ==
                True
            )
        )

        return result.scalar_one_or_none()
    
    async def create(
        self,
        db: AsyncSession,
        deployment: ModelDeployment,
    ):

        db.add(
            deployment
        )

        await db.flush()

        await db.refresh(
            deployment
        )

        return deployment
    
    async def update(
        self,
        db: AsyncSession,
        deployment: ModelDeployment,
    ):

        await db.flush()

        await db.refresh(
            deployment
        )

        return deployment
    
    async def delete(
        self,
        db: AsyncSession,
        deployment: ModelDeployment,
    ):

        await db.delete(
            deployment
        )

    async def get_by_id(
        self,
        db: AsyncSession,
        deployment_id: int,
    ):

        result = await db.execute(

            select(
                ModelDeployment
            )

            .where(
                ModelDeployment.id
                ==
                deployment_id
            )
        )

        return result.scalar_one_or_none()
    
    async def get_latest(
        self,
        db: AsyncSession,
        model_version_id: int,
    ):

        result = await db.execute(

            select(
                ModelDeployment
            )

            .where(
                ModelDeployment.model_version_id
                ==
                model_version_id
            )

            .order_by(
                ModelDeployment.created_at.desc()
            )

            .limit(1)
        )

        return result.scalar_one_or_none()
    
    async def list_all(
        self,
        db: AsyncSession,
    ):

        result = await db.execute(

            select(
                ModelDeployment
            )

            .order_by(
                ModelDeployment.created_at.desc()
            )
        )

        return result.scalars().all()
    
    async def list_active(
        self,
        db: AsyncSession,
    ):

        result = await db.execute(

            select(
                ModelDeployment
            )

            .where(
                ModelDeployment.is_active
                ==
                True
            )

            .order_by(
                ModelDeployment.created_at.desc()
            )
        )

        return result.scalars().all()



model_deployment_repository = (
    ModelDeploymentRepository()
)