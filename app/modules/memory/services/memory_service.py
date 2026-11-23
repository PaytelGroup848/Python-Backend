
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

from sqlalchemy import select, desc
from app.db.database import AsyncSessionLocal
from app.db.redis_client import redis_client
from app.models.message import Message

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

            if memory:
                return [
                    json.loads(item)
                    for item in memory
                ]

            # Cache miss: Production Cache-Aside fallback to PostgreSQL
            conv_id = None
            if isinstance(session_id, int):
                conv_id = session_id
            elif isinstance(session_id, str) and session_id.isdigit():
                conv_id = int(session_id)

            if conv_id is not None:
                try:
                    async with AsyncSessionLocal() as session:
                        # Fetch the most recent N messages from DB
                        stmt = (
                            select(Message.role, Message.content, Message.created_at)
                            .where(Message.conversation_id == conv_id)
                            .order_by(desc(Message.id))
                            .limit(MAX_MEMORY_MESSAGES + 1)
                        )
                        result = await session.execute(stmt)
                        rows = result.all()

                        if rows:
                            # If the very last message in DB is an active user turn, exclude it from history
                            # because the active turn is explicitly appended by ContextBuilderService
                            if rows[0].role == "user":
                                candidate_rows = rows[1:MAX_MEMORY_MESSAGES + 1]
                            else:
                                candidate_rows = rows[:MAX_MEMORY_MESSAGES]

                            if candidate_rows:
                                chronological_rows = list(reversed(candidate_rows))
                                db_memory = []
                                pipe = redis_client.pipeline()

                                for r in chronological_rows:
                                    payload = {
                                        "role": r.role,
                                        "content": r.content or "",
                                        "timestamp": (
                                            r.created_at.isoformat()
                                            if r.created_at
                                            else datetime.utcnow().isoformat()
                                        )
                                    }
                                    db_memory.append(payload)
                                    pipe.rpush(key, json.dumps(payload))

                                pipe.ltrim(key, -MAX_MEMORY_MESSAGES, -1)
                                pipe.expire(key, MEMORY_TTL)
                                try:
                                    await pipe.execute()
                                except Exception as pipe_err:
                                    logger.warning(
                                        f"Failed to warm Redis memory cache for session {session_id}: {pipe_err}"
                                    )

                                return db_memory

                except Exception as db_err:
                    logger.exception(
                        "PostgreSQL memory fallback failed",
                        extra={"session_id": session_id, "error": str(db_err)}
                    )

            return []

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
