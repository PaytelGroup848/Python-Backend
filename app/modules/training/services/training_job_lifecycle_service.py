from datetime import datetime

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.training.models.training_job import (
    TrainingJob,
)

from app.modules.training.repositories.training_job_repository import (
    training_job_repository,
)

from app.shared.constants.training_status import (
    TrainingStatus,
)

from app.shared.exceptions.business_exception import (
    BusinessException,
)


class TrainingJobLifecycleService:

    async def mark_queued(
        self,
        db: AsyncSession,
        training_job: TrainingJob,
    ) -> TrainingJob:

        if (
            training_job.status
            !=
            TrainingStatus.PENDING
        ):

            raise BusinessException(
                "Only pending jobs can be queued."
            )

        training_job.status = (
            TrainingStatus.QUEUED
        )

        if hasattr(
            training_job,
            "queued_at",
        ):
            training_job.queued_at = (
                datetime.utcnow()
            )

        return await (
            training_job_repository
            .update(
                db=db,
                training_job=training_job,
            )
        )


    async def mark_running(
        self,
        db: AsyncSession,
        training_job: TrainingJob,
    ) -> TrainingJob:

        if (
            training_job.status
            !=
            TrainingStatus.QUEUED
        ):

            raise BusinessException(
                "Only queued jobs can start."
            )

        training_job.status = (
            TrainingStatus.RUNNING
        )

        if hasattr(
            training_job,
            "started_at",
        ):
            training_job.started_at = (
                datetime.utcnow()
            )

        return await (
            training_job_repository
            .update(
                db=db,
                training_job=training_job,
            )
        )


    async def mark_completed(
        self,
        db: AsyncSession,
        training_job: TrainingJob,
    ) -> TrainingJob:

        training_job.status = (
            TrainingStatus.COMPLETED
        )

        if hasattr(
            training_job,
            "completed_at",
        ):
            training_job.completed_at = (
                datetime.utcnow()
            )

            if hasattr(
                training_job,
                "failure_reason",
            ):
                training_job.failure_reason = None



        return await (
            training_job_repository
            .update(
                db=db,
                training_job=training_job,
            )
        )


    async def mark_failed(
        self,
        db: AsyncSession,
        training_job: TrainingJob,
        failure_reason: str | None = None,
    ) -> TrainingJob:

        training_job.status = (
            TrainingStatus.FAILED
        )

        if hasattr(
            training_job,
            "failed_at",
        ):
            training_job.failed_at = (
                datetime.utcnow()
            )

        if (
            failure_reason
            and
            hasattr(
                training_job,
                "failure_reason",
            )
        ):
            training_job.failure_reason = (
                failure_reason
            )

        return await (
            training_job_repository
            .update(
                db=db,
                training_job=training_job,
            )
        )


    async def mark_cancelled(
        self,
        db: AsyncSession,
        training_job: TrainingJob,
    ) -> TrainingJob:

        training_job.status = (
            TrainingStatus.CANCELLED
        )

        return await (
            training_job_repository
            .update(
                db=db,
                training_job=training_job,
            )
        )


    async def mark_retrying(
        self,
        db: AsyncSession,
        training_job: TrainingJob,
    ) -> TrainingJob:

        training_job.status = (
            TrainingStatus.RETRYING
        )

        if hasattr(
            training_job,
            "failure_reason",
        ):
            training_job.failure_reason = None

        if hasattr(
            training_job,
            "failed_at",
        ):
            training_job.failed_at = None

        if hasattr(
            training_job,
            "current_epoch",
        ):
            training_job.current_epoch = 0

        if hasattr(
            training_job,
            "current_step",
        ):
            training_job.current_step = 0

        if hasattr(
            training_job,
            "global_step",
        ):
            training_job.global_step = 0

        if hasattr(
            training_job,
            "processed_samples",
        ):
            training_job.processed_samples = 0

        if hasattr(
            training_job,
            "processed_tokens",
        ):
            training_job.processed_tokens = 0

        if hasattr(
            training_job,
            "current_loss",
        ):
            training_job.current_loss = None

        if hasattr(
            training_job,
            "learning_rate",
        ):
            training_job.learning_rate = None

        if hasattr(
            training_job,
            "last_checkpoint_path",
        ):
            training_job.last_checkpoint_path = None

        if hasattr(
            training_job,
            "last_checkpoint_at",
        ):
            training_job.last_checkpoint_at = None

        
        

        return await (
            training_job_repository
            .update(
                db=db,
                training_job=training_job,
            )
        )


training_job_lifecycle_service = (
    TrainingJobLifecycleService()
)