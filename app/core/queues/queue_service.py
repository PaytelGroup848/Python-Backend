from app.db.redis_client import (
    redis_client
)


MAX_PENDING_REQUESTS = 5


class QueueService:

    async def can_enqueue(

        self,

        user_id: str,
    ) -> bool:

        key = (
            f"queue:{user_id}"
        )

        count = await redis_client.get(
            key
        )

        count = (
            int(count)
            if count
            else 0
        )

        return (
            count
            < MAX_PENDING_REQUESTS
        )

    async def increment(

        self,

        user_id: str,
    ) -> None:

        key = (
            f"queue:{user_id}"
        )

        await redis_client.incr(
            key
        )

        await redis_client.expire(

            key,

            300,
        )

    async def decrement(

        self,

        user_id: str,
    ) -> None:

        key = (
            f"queue:{user_id}"
        )

        current = await redis_client.get(
            key
        )

        if (
            current
            and int(current) > 0
        ):

            await redis_client.decr(
                key
            )


queue_service = (
    QueueService()
)