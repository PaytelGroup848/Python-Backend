import json

from app.shared.redis.client import (
    redis_client
)


class RedisStreamService:

    async def publish(

        self,

        stream_name: str,

        data: dict,
    ):

        await redis_client.xadd(

            stream_name,

            {
                "data": json.dumps(data)
            }
        )

    async def consume(

        self,

        stream_name: str,

        group_name: str,

        consumer_name: str,
    ):

        try:

            await redis_client.xgroup_create(

                stream_name,

                group_name,

                id="0",

                mkstream=True,
            )

        except Exception:

            pass

        response = (
            await redis_client.xreadgroup(

                group_name,

                consumer_name,

                streams={
                    stream_name: ">"
                },

                count=1,

                block=5000,
            )
        )

        return response


redis_stream_service = (
    RedisStreamService()
)