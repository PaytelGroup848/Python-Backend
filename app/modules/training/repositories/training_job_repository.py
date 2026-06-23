from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.training.models.training_job import (
    TrainingJob
)




class TrainingJobRepository:

    async def create(

        self,

        db: AsyncSession,

        training_job: TrainingJob

    ):

        db.add(
            training_job
        )

        await db.flush()

        await db.refresh(
            training_job
        )

        return training_job

    async def get_by_id(

        self,

        db: AsyncSession,

        training_job_id: int

    ):

        result = await db.execute(

            select(
                TrainingJob
            )
            .where(
                TrainingJob.id
                ==
                training_job_id
            )
        )

        return result.scalar_one_or_none()

    async def list_all(

        self,

        db: AsyncSession

    ):

        result = await db.execute(
            select(
                TrainingJob
            )
        )

        return result.scalars().all()
    
    async def update(

        self,

        db: AsyncSession,

        training_job: TrainingJob

    ):

       

       

        return training_job


training_job_repository = (
    TrainingJobRepository()
)