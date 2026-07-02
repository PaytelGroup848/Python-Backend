
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

from app.db.redis_client import redis_client

logger = logging.getLogger(__name__)

MEMORY_TTL = 3600

MAX_MEMORY_MESSAGES = 20


class MemoryService:

    @staticmethod
    def _memory_key(
        session_id: str
    ) -> str:

        return (
            f"chat:memory:{session_id}"
        )

    async def save_memory(

        self,

        session_id: str,

        role: str,

        message: str,

    ) -> None:

        key = self._memory_key(
            session_id
        )

        try:

            payload = {

                "role": role,

                "content": message,

                "timestamp": (
                    datetime.utcnow()
                    .isoformat()
                )
            }

            pipe = redis_client.pipeline()

            # atomic append

            pipe.rpush(
                key,
                json.dumps(payload)
            )

            # keep latest messages only

            pipe.ltrim(
                key,
                -MAX_MEMORY_MESSAGES,
                -1
            )

            # refresh ttl

            pipe.expire(
                key,
                MEMORY_TTL
            )

            await pipe.execute()

        except Exception:

            logger.exception(
                "Memory save failed",
                extra={
                    "session_id": session_id
                }
            )

    async def get_memory(

        self,

        session_id: str,

    ) -> List[Dict[str, Any]]:

        key = self._memory_key(
            session_id
        )

        try:

            memory = await redis_client.lrange(
                key,
                0,
                -1
            )

            if not memory:

                return []

            return [

                json.loads(item)

                for item in memory
            ]

        except Exception:

            logger.exception(
                "Memory fetch failed",
                extra={
                    "session_id": session_id
                }
            )

            return []

    async def clear_memory(

        self,

        session_id: str,

    ) -> None:

        key = self._memory_key(
            session_id
        )

        try:

            await redis_client.delete(
                key
            )

        except Exception:

            logger.exception(
                "Memory clear failed",
                extra={
                    "session_id": session_id
                }
            )


memory_service = MemoryService()
