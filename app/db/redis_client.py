import redis.asyncio as redis
from app.core.config import settings

redis_client = redis.Redis(
    host=getattr(settings, "REDIS_HOST", "127.0.0.1"),
    port=getattr(settings, "REDIS_PORT", 6379),
    db=0,
    decode_responses=True
)


async def check_redis():
    try:
        await redis_client.ping()
        return True
    except Exception:
        return False
