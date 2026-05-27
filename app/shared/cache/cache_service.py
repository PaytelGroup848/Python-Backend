import json
import asyncio

from app.db.redis_client import (
    redis_client
)

class CacheService:

    def __init__(self):

        self.lock = asyncio.Lock()

    async def get(
        self,
        key: str,
    ):

        try:

            value = await redis_client.get(
                key
            )

            if not value:

                return None

            return json.loads(value)

        except Exception:

            return None

    async def set(

        self,

        key: str,

        value,

        ttl: int = 300,
    ):

        try:

            async with self.lock:

                await redis_client.setex(

                    key,

                    ttl,

                    json.dumps(value)
                )

        except Exception:

            pass

    async def delete(
        self,
        key: str,
    ):

        try:

            async with self.lock:

                await redis_client.delete(
                    key
                )

        except Exception:

            pass


cache_service = CacheService()