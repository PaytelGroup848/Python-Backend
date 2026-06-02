from app.modules.admin.repositories.queue_repository import (
    QueueRepository
)


class QueueService:

    def __init__(self):

        self.repository = QueueRepository()

    async def get_queues(self):

        return await (
            self.repository
            .get_queue_status()
        )