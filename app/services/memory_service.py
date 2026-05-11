import json

from app.db.redis_client import redis_client


MEMORY_TTL = 3600


def save_memory(
    session_id: str,
    role: str,
    message: str
):

    key = f"chat_memory:{session_id}"

    memory = redis_client.get(key)

    if memory:

        memory = json.loads(memory)

    else:

        memory = []

    memory.append({
        "role": role,
        "message": message
    })

    redis_client.setex(
        key,
        MEMORY_TTL,
        json.dumps(memory)
    )


def get_memory(
    session_id: str
):

    key = f"chat_memory:{session_id}"

    memory = redis_client.get(key)

    if not memory:

        return []

    return json.loads(memory)