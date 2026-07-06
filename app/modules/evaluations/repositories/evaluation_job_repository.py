from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.evaluations.models.evaluation_job import (
    EvaluationJob
)


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


evaluation_job_repository = (
    EvaluationJobRepository()
)