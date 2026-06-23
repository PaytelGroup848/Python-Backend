from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.training.repositories.training_job_repository import (
    training_job_repository
)


class TrainingStatusService:

    async def update_status(

        self,

        db: AsyncSession,

        training_job,

        status: str

    ):

        training_job.status = status

        await (
            training_job_repository
            .update(
                db,
                training_job
            )
        )

        return training_job


training_status_service = (
    TrainingStatusService()
)