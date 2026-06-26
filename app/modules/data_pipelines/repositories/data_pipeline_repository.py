from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.data_pipelines.models.data_pipeline import (
    DataPipeline
)


class DataPipelineRepository:

    async def create(
        self,
        db: AsyncSession,
        pipeline: DataPipeline
    ):

        db.add(
            pipeline
        )

        await db.flush()

        await db.refresh(
            pipeline
        )

        return pipeline

    async def get_by_id(
        self,
        db: AsyncSession,
        pipeline_id: int
    ):

        result = await db.execute(

            select(
                DataPipeline
            )
            .where(
                DataPipeline.id
                ==
                pipeline_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_pipeline_code(
        self,
        db: AsyncSession,
        pipeline_code: str
    ):

        result = await db.execute(

            select(
                DataPipeline
            )
            .where(
                DataPipeline.pipeline_code
                ==
                pipeline_code
            )
        )

        return result.scalar_one_or_none()
    
    async def exists_pipeline_code(

        self,

        db: AsyncSession,

        pipeline_code: str

    ):

        result = await db.execute(
 
            select(
                DataPipeline.id
            )
            .where(
                DataPipeline.pipeline_code
                == pipeline_code
            )
        )

        pipeline_id = result.scalar_one_or_none()

        return pipeline_id is not None

    async def list_by_corpus(
        self,
        db: AsyncSession,
        corpus_id: int
    ):

        result = await db.execute(

            select(
                DataPipeline
            )
            .where(
                DataPipeline.corpus_id
                ==
                corpus_id
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
                DataPipeline
            )
            .where(
                DataPipeline.status
                ==
                status
            )
        )

        return result.scalars().all()

    async def list_all(
        self,
        db: AsyncSession
    ):

        result = await db.execute(

            select(
                DataPipeline
            )
        )

        return result.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        pipeline: DataPipeline
    ):

        await db.flush()

        await db.refresh(
            pipeline
        )

        return pipeline

    async def delete(
        self,
        db: AsyncSession,
        pipeline: DataPipeline
    ):

        await db.delete(
            pipeline
        )

        await db.flush()


data_pipeline_repository = (
    DataPipelineRepository()
)