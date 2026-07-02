from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException
from app.shared.exceptions.not_found_exception import (
    NotFoundException
)

from app.shared.constants.training_status import (
    TrainingStatus
)

from app.modules.training.repositories.training_job_repository import (
    training_job_repository
)

from app.modules.training_providers.services.training_provider_service import (
    training_provider_service
)

from app.core.queues.training_queue import (
    training_queue
)


class TrainingDispatchService:

    async def dispatch(

        self,

        db: AsyncSession,

        training_job_id: int

    ):

        job = await (
            training_job_repository
            .get_by_id(
                db=db,
                training_job_id=training_job_id
            )
        )

        if not job:

            raise HTTPException(
                status_code=404,
                detail=f"Training job {training_job_id} not found"
            )

        provider = await (
            training_provider_service
            .get_provider(
                db=db,
                provider_id=job.training_provider_id
            )
        )

        if not provider:
            raise ValueError(
                "Training provider not found"
            )

        if not provider.is_active:
            raise ValueError(
                "Training provider is inactive"
            )

        job.status = "QUEUED"

        if job.status != "PENDING":

            raise ValueError(
                f"Training job is in '{job.status}' state and cannot be dispatched."
            )

        await (
            training_job_repository
            .update(
                db=db,
                training_job=job
            )
        )

        await db.commit()

        await (
            training_queue
            .enqueue(
                training_job_id
            )
        )

        return {
            "success": True,
            "training_job_id": training_job_id,
            "provider": provider.code,
            "message": "Training job queued"
        }


training_dispatch_service = (
    TrainingDispatchService()
)