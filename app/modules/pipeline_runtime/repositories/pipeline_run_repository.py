from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.pipeline_runtime.models.pipeline_run import (
    PipelineRun
)


class PipelineRunRepository:

    async def create(
        self,
        db: AsyncSession,
        pipeline_run: PipelineRun
    ):

        db.add(
            pipeline_run
        )

        await db.flush()

        await db.refresh(
            pipeline_run
        )

        return pipeline_run

    async def get_by_id(
        self,
        db: AsyncSession,
        pipeline_run_id: int
    ):

        result = await db.execute(

            select(
                PipelineRun
            )
            .where(
                PipelineRun.id
                ==
                pipeline_run_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_run_code(
        self,
        db: AsyncSession,
        run_code: str
    ):

        result = await db.execute(

            select(
                PipelineRun
            )
            .where(
                PipelineRun.run_code
                ==
                run_code
            )
        )

        return result.scalar_one_or_none()

    async def list_all(
        self,
        db: AsyncSession
    ):

        result = await db.execute(

            select(
                PipelineRun
            )
            .order_by(
                PipelineRun.created_at.desc()
            )
        )

        return result.scalars().all()

    async def list_by_pipeline(
        self,
        db: AsyncSession,
        pipeline_id: int
    ):

        result = await db.execute(

            select(
                PipelineRun
            )
            .where(
                PipelineRun.pipeline_id
                ==
                pipeline_id
            )
            .order_by(
                PipelineRun.created_at.desc()
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
                PipelineRun
            )
            .where(
                PipelineRun.status
                ==
                status
            )
            .order_by(
                PipelineRun.created_at.desc()
            )
        )

        return result.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        pipeline_run: PipelineRun
    ):

        await db.flush()

        await db.refresh(
            pipeline_run
        )

        return pipeline_run

    async def delete(
        self,
        db: AsyncSession,
        pipeline_run: PipelineRun
    ):

        await db.delete(
            pipeline_run
        )

        await db.flush()


pipeline_run_repository = (
    PipelineRunRepository()
)