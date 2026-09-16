import logging
from app.db.redis_client import redis_client

logger = logging.getLogger(__name__)

MAX_LOGIN_ATTEMPTS = 5
LOCK_TIME_SECONDS = 900  # 15 min


def get_failed_key(email, ip):
    return f"failed:{email}:{ip}"


async def is_locked(email, ip):
    try:
        key = get_failed_key(email, ip)
        attempts = await redis_client.get(key)
        if attempts and int(attempts) >= MAX_LOGIN_ATTEMPTS:
            return True
        return False
    except Exception as e:
        logger.warning(
            f"SECURITY ALERT: Redis connection unavailable; lockout and rate-limiting protection degraded for email={email}, ip={ip}: {e}"
        )
        # Fail-open for availability so transient Redis drops do not take down authentication
        return False


async def record_failed_attempt(email, ip):
    try:
        key = get_failed_key(email, ip)
        current = await redis_client.get(key)
        current = int(current) if current else 0
        current += 1
        await redis_client.setex(
            key,
            LOCK_TIME_SECONDS,
            current
        )
    except Exception as e:
        logger.warning(
            f"SECURITY ALERT: Failed to record login attempt in Redis for email={email}, ip={ip}: {e}"
        )


async def clear_failed_attempts(email, ip):
    try:
        key = get_failed_key(email, ip)
        await redis_client.delete(key)
    except Exception as e:
        logger.warning(
            f"Failed to clear login attempts in Redis for email={email}, ip={ip}: {e}"
        )