import json
from typing import List, Dict, Any

from app.db.redis_client import redis_client


MEMORY_TTL = 3600

MAX_MEMORY_MESSAGES = 20


class MemoryService:

    async def save_memory(

        self,

        session_id: str,

        role: str,

        message: str,

    ) -> None:

        key = (
            f"chat:memory:{session_id}"
        )

        try:

            memory = await redis_client.get(
                key
            )

            if memory:

                memory = json.loads(
                    memory
                )

            else:

                memory = []

            memory.append({

                "role": role,

                "content": message,
            })

            memory = memory[
                -MAX_MEMORY_MESSAGES:
            ]

            await redis_client.setex(

                key,

                MEMORY_TTL,

                json.dumps(memory),
            )

        except Exception as e:

            print(
                "Memory save failed:"
            )

            print(str(e))

    async def get_memory(

        self,

        session_id: str,

    ) -> List[Dict[str, Any]]:

        key = (
            f"chat:memory:{session_id}"
        )

        try:

            memory = await redis_client.get(
                key
            )

            if not memory:

                return []

            return json.loads(
                memory
            )

        except Exception as e:

            print(
                "Memory fetch failed:"
            )

            print(str(e))

            return []

    async def clear_memory(

        self,

        session_id: str,

    ) -> None:

        key = (
            f"chat:memory:{session_id}"
        )

        try:

            await redis_client.delete(
                key
            )

        except Exception as e:

            print(
                "Memory clear failed:"
            )

            print(str(e))


memory_service = (
    MemoryService()
)