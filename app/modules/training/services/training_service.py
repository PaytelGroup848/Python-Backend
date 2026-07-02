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
                db=db,
                training_job=training_job
            )
        )

        await db.commit()

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
    
    async def list_training_jobs(

        self,

        db: AsyncSession

    ):

        return await (
            training_job_repository
            .list_all(
                db=db
            )
        )
    
    async def list_training_jobs_by_status(

        self,

        db: AsyncSession,

        status: str

    ):

        return await (
            training_job_repository
            .list_by_status(
                db=db,
                status=status
            )
        )
    
    async def list_training_jobs_by_dataset(

        self,

        db: AsyncSession,

        dataset_id: int

    ):

        return await (
            training_job_repository
            .list_by_dataset(
                db=db,
                dataset_id=dataset_id
            )
        )
    
    async def list_training_jobs_by_model(

        self,

        db: AsyncSession,

        base_model_id: int

    ):

        return await (
            training_job_repository
            .list_by_base_model(
                db=db,
                base_model_id=base_model_id
            )
        )
    
    async def update_training_job(

        self,

        db: AsyncSession,

        training_job: TrainingJob

    ):

        training_job = await (
            training_job_repository
            .update(
                db=db,
                training_job=training_job
            )
        )

        await db.commit()

        return training_job
    
    async def delete_training_job(

        self,

        db: AsyncSession,

        training_job_id: int

    ) -> bool:

        training_job = await (
            training_job_repository
            .get_by_id(
                db=db,
                training_job_id=training_job_id
            )
        )

        if training_job is None:

            return False

        await (
            training_job_repository
            .delete(
                db=db,
                training_job=training_job
            )
        )

        await db.commit()

        return True


training_service = (
    TrainingService()
)