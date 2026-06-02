class WorkerRepository:

    async def get_worker_status(self):

        return [
            {
                "name": "Chat Request Worker",
                "status": "running",
                "queue_size": 2,
            },
            {
                "name": "Chat Response Worker",
                "status": "running",
                "queue_size": 1,
            },
            {
                "name": "Embedding Worker",
                "status": "running",
                "queue_size": 0,
            },
            {
                "name": "RAG Worker",
                "status": "running",
                "queue_size": 3,
            },
        ]