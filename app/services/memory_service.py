import json

from app.db.redis_client import redis_client

MEMORY_TTL = 3600


async def save_memory(
    session_id: str,
    role: str,
    message: str
):

    key = f"chat_memory:{session_id}"

    memory = await redis_client.get(key)

    if memory:

        memory = json.loads(memory)

    else:

        memory = []

    memory.append({
        "role": role,
        "message": message
    })

    await redis_client.setex(
        key,
        MEMORY_TTL,
        json.dumps(memory)
    )


async def get_memory(
    session_id: str
):

    key = f"chat_memory:{session_id}"

    memory = await redis_client.get(key)

    if not memory:

        return []

    return json.loads(memory)

async def clear_memory(
    session_id: str
):

    key = f"chat_memory:{session_id}"

    await redis_client.delete(key)