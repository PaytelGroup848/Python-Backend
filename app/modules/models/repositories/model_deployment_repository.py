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


model_deployment_repository = (
    ModelDeploymentRepository()
)