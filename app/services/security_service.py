from app.db.redis_client import redis_client

MAX_LOGIN_ATTEMPTS = 5
LOCK_TIME_SECONDS = 900  # 15 min


def get_failed_key(email, ip):
    return f"failed:{email}:{ip}"


async def is_locked(email, ip):

    key = get_failed_key(email, ip)

    attempts = await redis_client.get(key)

    if attempts and int(attempts) >= MAX_LOGIN_ATTEMPTS:
        return True

    return False


async def record_failed_attempt(email, ip):

    key = get_failed_key(email, ip)

    current = await redis_client.get(key)

    current = int(current) if current else 0

    current += 1

    await redis_client.setex(
        key,
        LOCK_TIME_SECONDS,
        current
    )


async def clear_failed_attempts(email, ip):

    key = get_failed_key(email, ip)

    await redis_client.delete(key)