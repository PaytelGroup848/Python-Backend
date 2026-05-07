import redis

redis_client = redis.Redis(
    host="redis",
    port=6379,
    db=0,
    decode_responses=True
)

# Check connection (optional fallback)
try:
    redis_client.ping()
    REDIS_AVAILABLE = True
    print(" Redis connected")
except:
    REDIS_AVAILABLE = False
    print(" Redis not available, using fallback")