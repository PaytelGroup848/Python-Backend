import redis.asyncio as redis

redis_client = redis.Redis(
    host="redis",
    port=6379,
    db=0,
    decode_responses=True
)

# Check connection
async def check_redis():

    try:

        await redis_client.ping()

        print("Redis connected")

        return True

    except Exception:

        print("Redis not available")

        return False