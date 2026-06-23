import json

from redis.asyncio import Redis

from app.core.config import settings


class ArtifactQueue:

    QUEUE_NAME = "artifact_jobs"

    def __init__(self):

        self.redis = Redis(

            host=settings.REDIS_HOST,

            port=settings.REDIS_PORT,

            decode_responses=True
        )

    async def enqueue(

        self,

        artifact_id: int

    ):

        payload = {

            "artifact_id":
                artifact_id
        }

        await self.redis.rpush(

            self.QUEUE_NAME,

            json.dumps(payload)
        )

    async def dequeue(self):

        result = await self.redis.blpop(

            self.QUEUE_NAME
        )

        if not result:

            return None

        _, payload = result

        return json.loads(
            payload
        )


artifact_queue = (
    ArtifactQueue()
)