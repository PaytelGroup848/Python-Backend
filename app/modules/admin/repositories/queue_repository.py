class QueueRepository:

    async def get_queue_status(self):

        return {
            "chat_queue": 12,
            "embedding_queue": 3,
            "rag_queue": 1,
            "voice_queue": 0,
        }