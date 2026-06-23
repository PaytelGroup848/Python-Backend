import asyncio

from app.db.database import (
    AsyncSessionLocal
)

from app.core.queues.training_queue import (
    training_queue
)

from app.modules.training_runtime.services.training_executor_service import (
    training_executor_service
)


async def worker():

    while True:

        payload = await (
            training_queue
            .dequeue()
        )

        if not payload:

            continue

        training_job_id = (
            payload["training_job_id"]
        )

        async with AsyncSessionLocal() as db:

            await (
                training_executor_service
                .execute(
                    db=db,
                    training_job_id=training_job_id
                )
            )

            


if __name__ == "__main__":

    asyncio.run(
        worker()
    )