import asyncio
import logging

from sqlalchemy.exc import SQLAlchemyError

from app.db.database import (
    AsyncSessionLocal,
)

from app.core.queues.training_queue import (
    training_queue,
)

from app.modules.training.repositories.training_job_repository import (
    training_job_repository,
)

from app.modules.training_runtime.services.training_executor_service import (
    training_executor_service,
)

from app.shared.constants.training_status import (
    TrainingStatus,
)

from app.modules.training.services.training_job_lifecycle_service import (
    training_job_lifecycle_service,
)


logger = logging.getLogger(__name__)


async def worker():

    #logger.info(
     #   "Training worker started."
    #)
    print("WORKER STARTED", flush=True)

    while True:

        payload = await (
            training_queue
            .dequeue()
        )

        logger.info("========== PAYLOAD: %s ==========", payload)

        if not payload:
            continue

        training_job_id = payload.get(
            "training_job_id"
        )

        if training_job_id is None:

            logger.warning(
                "Queue payload missing training_job_id."
            )

            continue

        logger.info(
            "Dequeued training job %s",
            training_job_id,
        )

        async with AsyncSessionLocal() as db:

            try:

                job = await (
                    training_job_repository
                    .get_by_id(
                        db=db,
                        training_job_id=training_job_id,
                    )
                )

                if job is None:

                    logger.warning(
                        "Training job %s not found.",
                        training_job_id,
                    )

                    continue

                if (
                    job.status
                    !=
                    TrainingStatus.QUEUED
                ):

                    logger.warning(
                        "Training job %s is in '%s' state.",
                        training_job_id,
                        job.status,
                    )

                    continue


                await (
                    training_job_lifecycle_service
                    .mark_running(
                        db=db,
                        training_job=job,
                    )
                )

                logger.info("========== JOB MARKED RUNNING ==========")

                await db.commit()

                logger.info("========== RUNNING COMMIT DONE ==========")



                logger.info(
                    "Training job %s started.",
                    training_job_id,
                )

                print("BEFORE EXECUTE", flush=True)
                print(f"[WORKER] Before executor job={training_job_id}", flush=True)

                await (
                    training_executor_service
                    .execute(
                        db=db,
                        training_job_id=training_job_id,
                    )
                )
                print(f"[WORKER] After executor job={training_job_id}", flush=True)

                print("AFTER EXECUTE", flush=True)

                await (
                    training_job_lifecycle_service
                    .mark_completed(
                        db=db,
                        training_job=job,
                    )
                )

                await db.commit()

                logger.info(
                    "Training job %s completed.",
                    training_job_id,
                )

            except Exception as ex:

                print("EXCEPTION:", repr(ex), flush=True)

                await db.rollback()

                try:

                    job = await (
                        training_job_repository
                        .get_by_id(
                            db=db,
                            training_job_id=training_job_id,
                        )
                    )

                    if job is not None:

                        await (
                            training_job_lifecycle_service
                            .mark_failed(
                                db=db,
                                training_job=job,
                                failure_reason=str(ex),
                            )
                        )

                        await db.commit()

                except SQLAlchemyError:

                    await db.rollback()

                    logger.exception(
                        "Unable to update failed state for training job %s.",
                        training_job_id,
                    )

                logger.exception(
                    "Training job %s failed: %s",
                    training_job_id,
                    ex,
                )


if __name__ == "__main__":

    asyncio.run(
        worker()
    )