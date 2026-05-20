import time

from app.db.redis_client import (
    redis_client,
)

RATE_LIMIT = 60

WINDOW_SECONDS = 60


async def check_rate_limit(
    user_id: str,
):

    now = int(time.time())

    window_start = (
        now - WINDOW_SECONDS
    )

    key = (
        f"rate_limit:{user_id}"
    )

    # remove old requests
    await redis_client.zremrangebyscore(
        key,
        0,
        window_start
    )

    # count active requests
    request_count = (
        await redis_client.zcard(key)
    )

    if request_count >= RATE_LIMIT:
        return False

    # add current request
    await redis_client.zadd(
        key,
        {str(now): now}
    )

    # auto cleanup
    await redis_client.expire(
        key,
        WINDOW_SECONDS
    )

    return True