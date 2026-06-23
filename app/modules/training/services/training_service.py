from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.training.models.training_job import (
    TrainingJob
)

from app.modules.training.repositories.training_job_repository import (
    training_job_repository
)

from app.modules.training.schemas.training_job_create import (
    TrainingJobCreate
)


class TrainingService:

    async def create_training_job(

        self,

        db: AsyncSession,

        data: TrainingJobCreate

    ):

        training_job = TrainingJob(
            **data.model_dump()
        )

        training_job = await (
            training_job_repository
            .create(
                db,
                training_job
            )
        )

        await db.commit()

        await db.refresh(
            training_job
        )

        return training_job

    async def get_training_job(

        self,

        db: AsyncSession,

        training_job_id: int

    ):

        return await (
            training_job_repository
            .get_by_id(
                db,
                training_job_id
            )
        )


training_service = (
    TrainingService()
)