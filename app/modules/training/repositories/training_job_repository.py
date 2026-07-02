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
    
    async def update(

        self,

        db: AsyncSession,

        training_job: TrainingJob

    ):

        await db.flush()

        await db.refresh(
            training_job
        )

        return training_job
    
    async def delete(

        self,

        db: AsyncSession,

        training_job: TrainingJob

    ):

        await db.delete(
            training_job
        )
    


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
    
    async def get_latest(

        self,

        db: AsyncSession

    ):

        result = await db.execute(

            select(
                TrainingJob
            )

            .order_by(
                TrainingJob.created_at.desc()
            )

            .limit(1)

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

            .order_by(
                TrainingJob.created_at.desc()
            )

        )

        return result.scalars().all()
    
    async def list_by_status(

        self,

        db: AsyncSession,

        status: str

    ):

        result = await db.execute(

            select(
                TrainingJob
            )

            .where(
                TrainingJob.status
                ==
                status
            )

            .order_by(
                TrainingJob.created_at.desc()
            )

        )

        return result.scalars().all()
    
    async def list_by_dataset(

        self,

        db: AsyncSession,

        dataset_id: int

    ):

        result = await db.execute(

            select(
                TrainingJob
            )

            .where(
                TrainingJob.dataset_id
                ==
                dataset_id
            )

            .order_by(
                TrainingJob.created_at.desc()
            )

        )

        return result.scalars().all()
    
    async def list_by_base_model(

        self,

        db: AsyncSession,

        base_model_id: int

    ):

        result = await db.execute(

            select(
                TrainingJob
            )

            .where(
                TrainingJob.base_model_id
                ==
                base_model_id
            )

            .order_by(
                TrainingJob.created_at.desc()
            )

        )

        return result.scalars().all()
    


training_job_repository = (
    TrainingJobRepository()
)