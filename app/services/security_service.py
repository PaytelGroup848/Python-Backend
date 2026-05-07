from app.db.redis_client import redis_client

MAX_LOGIN_ATTEMPTS = 5
LOCK_TIME_SECONDS = 900  # 15 min

def get_failed_key(email, ip):
    return f"failed:{email}:{ip}"

def is_locked(email, ip):

    key = get_failed_key(email, ip)

    attempts = redis_client.get(key)

    if attempts and int(attempts) >= MAX_LOGIN_ATTEMPTS:
        return True

    return False

def record_failed_attempt(email, ip):

    key = get_failed_key(email, ip)

    current = redis_client.get(key)

    current = int(current) if current else 0

    current += 1

    redis_client.setex(
        key,
        LOCK_TIME_SECONDS,
        current
    )

def clear_failed_attempts(email, ip):

    key = get_failed_key(email, ip)

    redis_client.delete(key)