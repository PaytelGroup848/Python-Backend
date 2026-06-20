import hashlib
import json

from app.modules.memory.repositories.cag_repository import (
    cag_repository
)


class CAGService:

    def _key(
        self,
        assistant_id: int,
        query: str
    ):

        digest = hashlib.sha256(
            query.lower().encode()
        ).hexdigest()

        return (
            f"cag:"
            f"{assistant_id}:"
            f"{digest}"
        )

    async def get_response(
        self,
        assistant_id: int,
        query: str
    ):

        key = self._key(
            assistant_id,
            query
        )

        cached = await (
            cag_repository.get(
                key
            )
        )

        if not cached:

            return None

        return json.loads(
            cached
        )

    async def save_response(
        self,
        assistant_id: int,
        query: str,
        response: str
    ):

        key = self._key(
            assistant_id,
            query
        )

        await (
            cag_repository.set(
                key,
                json.dumps(
                    {
                        "response":
                        response
                    }
                )
            )
        )


cag_service = (
    CAGService()
)