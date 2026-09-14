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
        key = f"queue:{user_id}"
        await redis_client.incr(key)
        await redis_client.expire(key, 180)

    async def decrement(
        self,
        user_id: str,
    ) -> None:
        key = f"queue:{user_id}"
        try:
            lua_script = """
            local cur = redis.call('get', KEYS[1])
            if cur and tonumber(cur) > 1 then
                return redis.call('decr', KEYS[1])
            else
                redis.call('del', KEYS[1])
                return 0
            end
            """
            await redis_client.eval(lua_script, 1, key)
        except Exception:
            current = await redis_client.get(key)
            if current and int(current) > 1:
                await redis_client.decr(key)
            else:
                await redis_client.delete(key)


queue_service = (
    QueueService()
)