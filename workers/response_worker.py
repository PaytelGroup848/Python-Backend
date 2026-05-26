import asyncio
import json

from app.shared.redis.stream_service import (
    redis_stream_service
)

from app.shared.redis.client import (
    redis_client
)

from app.shared.constants.streams import (
    CHAT_RESPONSE_STREAM
)

from app.modules.chat.services.ws_manager import (
    ws_manager
)


GROUP_NAME = (
    "response_workers"
)

CONSUMER_NAME = (
    "response_worker_1"
)


async def process_events():

    while True:

        response = (
            await redis_stream_service.consume(

                CHAT_RESPONSE_STREAM,

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

                request_id = (
                    data["request_id"]
                )

                websocket = (
                    ws_manager
                    .get_connection(
                        request_id
                    )
                )

                if websocket:

                    try:

                        await websocket.send_json(
                            data
                        )

                    except Exception:

                        pass

                await redis_client.xack(

                    CHAT_RESPONSE_STREAM,

                    GROUP_NAME,

                    message_id,
                )


asyncio.run(
    process_events()
)