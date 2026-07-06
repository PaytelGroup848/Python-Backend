from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.pipeline_runtime.models.pipeline_execution_artifact_edge import (
    PipelineExecutionArtifactEdge,
)


class PipelineExecutionArtifactEdgeRepository:

    async def create(
        self,
        db: AsyncSession,
        edge: PipelineExecutionArtifactEdge,
    ) -> PipelineExecutionArtifactEdge:

        db.add(edge)

        await db.flush()
        await db.refresh(edge)

        return edge

    async def get_existing(
        self,
        db: AsyncSession,
        parent_artifact_id: int,
        child_artifact_id: int,
        relation_type: str,
    ) -> PipelineExecutionArtifactEdge | None:

        result = await db.execute(
            select(
                PipelineExecutionArtifactEdge
            )
            .where(
                PipelineExecutionArtifactEdge.parent_artifact_id
                ==
                parent_artifact_id,
                PipelineExecutionArtifactEdge.child_artifact_id
                ==
                child_artifact_id,
                PipelineExecutionArtifactEdge.relation_type
                ==
                relation_type,
            )
        )

        return result.scalar_one_or_none()

    async def list_parents(
        self,
        db: AsyncSession,
        child_artifact_id: int,
    ) -> Sequence[PipelineExecutionArtifactEdge]:

        result = await db.execute(
            select(
                PipelineExecutionArtifactEdge
            )
            .where(
                PipelineExecutionArtifactEdge.child_artifact_id
                ==
                child_artifact_id
            )
            .order_by(
                PipelineExecutionArtifactEdge.id.asc()
            )
        )

        return result.scalars().all()

    async def list_children(
        self,
        db: AsyncSession,
        parent_artifact_id: int,
    ) -> Sequence[PipelineExecutionArtifactEdge]:

        result = await db.execute(
            select(
                PipelineExecutionArtifactEdge
            )
            .where(
                PipelineExecutionArtifactEdge.parent_artifact_id
                ==
                parent_artifact_id
            )
            .order_by(
                PipelineExecutionArtifactEdge.id.asc()
            )
        )

        return result.scalars().all()


pipeline_execution_artifact_edge_repository = (
    PipelineExecutionArtifactEdgeRepository()
)