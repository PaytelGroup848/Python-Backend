from app.modules.admin.repositories.worker_repository import (
    WorkerRepository
)


class WorkerService:

    def __init__(self):

        self.repository = (
            WorkerRepository()
        )

    async def get_workers(self):

        return {
            "workers":
                await self.repository
                .get_worker_status()
        }