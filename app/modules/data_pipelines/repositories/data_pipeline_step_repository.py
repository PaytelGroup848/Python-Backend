from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.data_pipelines.models.data_pipeline_step import (
    DataPipelineStep
)


class DataPipelineStepRepository:

    async def create(
        self,
        db: AsyncSession,
        pipeline_step: DataPipelineStep
    ):

        db.add(
            pipeline_step
        )

        await db.flush()

        await db.refresh(
            pipeline_step
        )

        return pipeline_step

    async def get_by_id(
        self,
        db: AsyncSession,
        pipeline_step_id: int
    ):

        result = await db.execute(

            select(
                DataPipelineStep
            )
            .where(
                DataPipelineStep.id
                ==
                pipeline_step_id
            )
        )

        return result.scalar_one_or_none()

    
    async def get_by_pipeline_and_step_code(
        self,
        db: AsyncSession,
        pipeline_id: int,
        step_code: str
    ):

        result = await db.execute(

            select(
                DataPipelineStep
            )
            .where(
                DataPipelineStep.pipeline_id
                ==
                pipeline_id,

                DataPipelineStep.step_code
                ==
                step_code
            )
        )

        return result.scalar_one_or_none()
    
    async def get_by_pipeline_and_order(
        self,
        db: AsyncSession,
        pipeline_id: int,
        step_order: int
    ):

        result = await db.execute(

            select(
                DataPipelineStep
            )
            .where(
                DataPipelineStep.pipeline_id
                ==
                pipeline_id,

                DataPipelineStep.step_order
                ==
                step_order
            )
        )

        return result.scalar_one_or_none()


    async def list_by_pipeline(
        self,
        db: AsyncSession,
        pipeline_id: int
    ):

        result = await db.execute(

            select(
                DataPipelineStep
            )
            .where(
                DataPipelineStep.pipeline_id
                ==
                pipeline_id
            )
            .order_by(
                DataPipelineStep.step_order.asc()
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
                DataPipelineStep
            )
            .where(
                DataPipelineStep.status
                ==
                status
            )
        )

        return result.scalars().all()
    
    async def list_by_runtime_code(
        self,
        db: AsyncSession,
        runtime_code: str
    ):

        result = await db.execute(

            select(
                DataPipelineStep
            )
            .where(
                DataPipelineStep.runtime_code
                ==
                runtime_code
            )
        )

        return result.scalars().all()

    
    async def update(
        self,
        db: AsyncSession,
        pipeline_step: DataPipelineStep
    ):

        await db.flush()

        await db.refresh(
            pipeline_step
        )

        return pipeline_step

    async def delete(
        self,
        db: AsyncSession,
        pipeline_step: DataPipelineStep
    ):

        await db.delete(
            pipeline_step
        )

        await db.flush()


data_pipeline_step_repository = (
    DataPipelineStepRepository()
)