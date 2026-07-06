from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.pipeline_runtime.models.pipeline_execution_artifact import (
    PipelineExecutionArtifact,
)


class PipelineExecutionArtifactRepository:

    async def create(
        self,
        db: AsyncSession,
        artifact: PipelineExecutionArtifact,
    ) -> PipelineExecutionArtifact:

        db.add(artifact)

        await db.flush()
        await db.refresh(artifact)

        return artifact

    async def get_by_id(
        self,
        db: AsyncSession,
        artifact_id: int,
    ) -> PipelineExecutionArtifact | None:

        result = await db.execute(
            select(
                PipelineExecutionArtifact
            )
            .where(
                PipelineExecutionArtifact.id
                ==
                artifact_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_code(
        self,
        db: AsyncSession,
        pipeline_run_id: int,
        artifact_code: str,
    ) -> PipelineExecutionArtifact | None:

        result = await db.execute(
            select(
                PipelineExecutionArtifact
            )
            .where(
                PipelineExecutionArtifact.pipeline_run_id
                ==
                pipeline_run_id,
                PipelineExecutionArtifact.artifact_code
                ==
                artifact_code,
            )
        )

        return result.scalar_one_or_none()

    async def list_by_run(
        self,
        db: AsyncSession,
        pipeline_run_id: int,
    ) -> Sequence[PipelineExecutionArtifact]:

        result = await db.execute(
            select(
                PipelineExecutionArtifact
            )
            .where(
                PipelineExecutionArtifact.pipeline_run_id
                ==
                pipeline_run_id
            )
            .order_by(
                PipelineExecutionArtifact.id.asc()
            )
        )

        return result.scalars().all()

    async def list_by_run_and_type(
        self,
        db: AsyncSession,
        pipeline_run_id: int,
        artifact_type: str,
        status: str | None = None,
    ) -> Sequence[PipelineExecutionArtifact]:

        statement = (
            select(
                PipelineExecutionArtifact
            )
            .where(
                PipelineExecutionArtifact.pipeline_run_id
                ==
                pipeline_run_id,
                PipelineExecutionArtifact.artifact_type
                ==
                artifact_type,
            )
        )

        if status is not None:

            statement = statement.where(
                PipelineExecutionArtifact.status
                ==
                status
            )

        result = await db.execute(
            statement.order_by(
                PipelineExecutionArtifact.id.asc()
            )
        )

        return result.scalars().all()

    async def list_by_producer_step_run(
        self,
        db: AsyncSession,
        producer_step_run_id: int,
    ) -> Sequence[PipelineExecutionArtifact]:

        result = await db.execute(
            select(
                PipelineExecutionArtifact
            )
            .where(
                PipelineExecutionArtifact.producer_step_run_id
                ==
                producer_step_run_id
            )
            .order_by(
                PipelineExecutionArtifact.id.asc()
            )
        )

        return result.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        artifact: PipelineExecutionArtifact,
    ) -> PipelineExecutionArtifact:

        await db.flush()
        await db.refresh(artifact)

        return artifact


pipeline_execution_artifact_repository = (
    PipelineExecutionArtifactRepository()
)