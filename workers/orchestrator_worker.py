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
)

from app.shared.events.event_types import (
    RAG_REQUEST_EVENT,
    LLM_REQUEST_EVENT,
)

GROUP_NAME = (
    "orchestrator_workers"
)

CONSUMER_NAME = (
    "orchestrator_1"
)


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

            messages = stream[1]

            for message in messages:

                message_id = message[0]

                payload = message[1]

                data = json.loads(
                    payload["data"]
                )

                await redis_stream_service.publish(

                    "rag_tasks",

                    {
                        "event_type":
                            RAG_REQUEST_EVENT,

                        **data,
                    },
                )

                await redis_stream_service.publish(

                    "llm_tasks",

                    {
                        "event_type":
                            LLM_REQUEST_EVENT,

                        **data,
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