from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.pipeline_runtime.models.pipeline_step_run import (
    PipelineStepRun
)


class PipelineStepRunRepository:

    async def create(
        self,
        db: AsyncSession,
        pipeline_step_run: PipelineStepRun
    ):

        db.add(
            pipeline_step_run
        )

        await db.flush()

        await db.refresh(
            pipeline_step_run
        )

        return pipeline_step_run

    async def get_by_id(
        self,
        db: AsyncSession,
        pipeline_step_run_id: int
    ):

        result = await db.execute(

            select(
                PipelineStepRun
            )
            .where(
                PipelineStepRun.id
                ==
                pipeline_step_run_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_step_run_code(
        self,
        db: AsyncSession,
        step_run_code: str
    ):

        result = await db.execute(

            select(
                PipelineStepRun
            )
            .where(
                PipelineStepRun.step_run_code
                ==
                step_run_code
            )
        )

        return result.scalar_one_or_none()

    async def get_by_pipeline_run_and_step(
        self,
        db: AsyncSession,
        pipeline_run_id: int,
        pipeline_step_id: int
    ):

        result = await db.execute(

            select(
                PipelineStepRun
            )
            .where(
                PipelineStepRun.pipeline_run_id
                ==
                pipeline_run_id,

                PipelineStepRun.pipeline_step_id
                ==
                pipeline_step_id
            )
        )

        return result.scalar_one_or_none()

    async def list_by_pipeline_run(
        self,
        db: AsyncSession,
        pipeline_run_id: int
    ):

        result = await db.execute(

            select(
                PipelineStepRun
            )
            .where(
                PipelineStepRun.pipeline_run_id
                ==
                pipeline_run_id
            )
            .order_by(
                PipelineStepRun.execution_order.asc()
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
                PipelineStepRun
            )
            .where(
                PipelineStepRun.status
                ==
                status
            )
            .order_by(
                PipelineStepRun.created_at.desc()
            )
        )

        return result.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        pipeline_step_run: PipelineStepRun
    ):

        await db.flush()

        await db.refresh(
            pipeline_step_run
        )

        return pipeline_step_run

    async def delete(
        self,
        db: AsyncSession,
        pipeline_step_run: PipelineStepRun
    ):

        await db.delete(
            pipeline_step_run
        )

        await db.flush()


pipeline_step_run_repository = (
    PipelineStepRunRepository()
)