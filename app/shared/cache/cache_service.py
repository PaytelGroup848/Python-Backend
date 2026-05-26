import json

from app.shared.redis.client import (
    redis_client
)


class CacheService:

    async def get(
        self,
        key: str,
    ):

        data = await redis_client.get(
            key
        )

        if not data:
            return None

        return json.loads(data)

    async def set(

        self,

        key: str,

        value,

        ttl: int = 300,
    ):

        await redis_client.setex(

            key,

            ttl,

            json.dumps(value),
        )

    async def delete(
        self,
        key: str,
    ):

        await redis_client.delete(
            key
        )


cache_service = CacheService()