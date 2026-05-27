import json

from app.db.redis_client import (
    redis_client
)

from app.shared.constants.streams import (
    EMBEDDING_STREAM
)


async def publish_embedding_job(
    payload: dict
):

    await redis_client.xadd(

        EMBEDDING_STREAM,

        {
            "data": json.dumps(
                payload
            )
        }
    )