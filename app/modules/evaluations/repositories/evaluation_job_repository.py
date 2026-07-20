from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.evaluations.models.evaluation_job import (
    EvaluationJob
)
from datetime import datetime


class EvaluationJobRepository:

    async def get_by_id(

        self,

        db: AsyncSession,

        evaluation_job_id: int

    ) -> EvaluationJob | None:

        result = await db.execute(

            select(
                EvaluationJob
            )
            .where(
                EvaluationJob.id
                ==
                evaluation_job_id
            )
        )

        return result.scalar_one_or_none()
    
    async def create(
        self,
        db: AsyncSession,
        evaluation_job: EvaluationJob,
    ) -> EvaluationJob:
        db.add(evaluation_job)
        await db.flush()
        await db.refresh(evaluation_job)
        return evaluation_job
    
    async def update_status(
        self,
        db: AsyncSession,
        evaluation_job: EvaluationJob,
        status: str,
    ) -> None:

        evaluation_job.status = status

        await db.flush()


    async def mark_started(
        self,
        db: AsyncSession,
        evaluation_job: EvaluationJob,
    ) -> None:

        evaluation_job.status = "running"
        evaluation_job.started_at = datetime.utcnow()

        await db.flush()

    async def save_metrics(
        self,
        db: AsyncSession,
        evaluation_job: EvaluationJob,
        metrics: dict,
        summary: dict,
    ) -> None:

        evaluation_job.metrics = metrics
        evaluation_job.summary = summary

        await db.flush()

    async def mark_completed(
        self,
        db: AsyncSession,
        evaluation_job: EvaluationJob,
        duration_ms: float,
    ) -> None:

        evaluation_job.status = "completed"
        evaluation_job.completed_at = datetime.utcnow()
        evaluation_job.duration_ms = duration_ms

        await db.flush()

    async def mark_failed(
        self,
        db: AsyncSession,
        evaluation_job: EvaluationJob,
        reason: str,
    ) -> None:

        evaluation_job.status = "failed"
        evaluation_job.failure_reason = reason
        evaluation_job.completed_at = datetime.utcnow()

        await db.flush()

    async def list_by_artifact(
        self,
        db: AsyncSession,
        artifact_id: int,
    ) -> list[EvaluationJob]:

        result = await db.execute(

            select(
                EvaluationJob
            ).where(
                EvaluationJob.artifact_id
                ==
                artifact_id
            )

        )

        return list(
            result.scalars().all()
        )


evaluation_job_repository = (
    EvaluationJobRepository()
)