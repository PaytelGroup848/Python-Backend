import asyncio

from app.db.redis_client import (
    redis_client
)

from app.shared.constants.streams import (
    CHAT_REQUEST_STREAM,
    EMBEDDING_STREAM
)


class QueueMetricsService:

    def __init__(self):

        self.lock = asyncio.Lock()

    async def get_stream_length(
        self,
        stream_name: str,
    ) -> int:

        try:

            return await redis_client.xlen(
                stream_name
            )

        except Exception:

            return 0

    async def get_queue_metrics(self):

        async with self.lock:

            chat_queue = await (
                self.get_stream_length(
                    CHAT_REQUEST_STREAM
                )
            )

            embedding_queue = await (
                self.get_stream_length(
                    EMBEDDING_STREAM
                )
            )

            return {

                "chat_queue_depth":
                    chat_queue,

                "embedding_queue_depth":
                    embedding_queue,
            }


queue_metrics_service = (
    QueueMetricsService()
)