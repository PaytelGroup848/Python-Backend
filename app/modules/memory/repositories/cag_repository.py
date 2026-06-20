from app.db.redis_client import (
    redis_client
)


class CAGRepository:

    async def get(
        self,
        key: str
    ):

        return await redis_client.get(
            key
        )

    async def set(
        self,
        key: str,
        value: str,
        ttl: int = 86400
    ):

        await redis_client.set(
            key,
            value,
            ex=ttl
        )


cag_repository = (
    CAGRepository()
)