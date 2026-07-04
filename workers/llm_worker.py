import asyncio
import json

from app.shared.redis.stream_service import (
    redis_stream_service
)

from app.shared.redis.client import (
    redis_client
)

from app.shared.constants.streams import (
    CHAT_REQUEST_STREAM,
    CHAT_RESPONSE_STREAM,
)

from app.modules.provider_runtime.manager.provider_runtime_manager import (
    provider_runtime_manager,
)


GROUP_NAME = "llm_workers"

CONSUMER_NAME = "worker_1"


async def process_events():

    while True:

        response = (
            await redis_stream_service.consume(

                CHAT_REQUEST_STREAM,

                GROUP_NAME,

                CONSUMER_NAME,
            )
        )

        if not response:
            continue

        for stream in response:

            stream_name = stream[0]

            messages = stream[1]

            for message in messages:

                message_id = message[0]

                payload = message[1]

                data = json.loads(
                    payload["data"]
                )

                request_id = (
                    data["request_id"]
                )

                conversation_id = (
                    data["conversation_id"]
                )

                user_message = (
                    data["message"]
                )

                await redis_stream_service.publish(

                    CHAT_RESPONSE_STREAM,

                    {
                        "type": "start",
                        "request_id": request_id,
                        "conversation_id": conversation_id,
                    },
                )

                async for chunk in (
                    provider_runtime_manager
                    .stream_response(
                        user_message
                    )
                ):

                    await redis_stream_service.publish(

                        CHAT_RESPONSE_STREAM,

                        {
                            "type": "chunk",
                            "request_id": request_id,
                            "conversation_id": conversation_id,
                            "content": chunk,
                        },
                    )

                await redis_stream_service.publish(

                    CHAT_RESPONSE_STREAM,

                    {
                        "type": "done",
                        "request_id": request_id,
                        "conversation_id": conversation_id,
                    },
                )

                await redis_client.xack(

                    CHAT_REQUEST_STREAM,

                    GROUP_NAME,

                    message_id,
                )


asyncio.run(
    process_events()
)