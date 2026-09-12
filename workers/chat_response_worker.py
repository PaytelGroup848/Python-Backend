
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

from app.shared.websocket.websocket_manager import websocket_manager


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

        
        print(
            "RESPONSE WORKER EVENTS:",
            response
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

                
                print(
                    "RESPONSE WORKER DATA:",
                    data
                )



                request_id = (
                    data["request_id"]
                )

                websocket = (
                    websocket_manager
                    .get_connection(
                        request_id
                    )
                )

                
                print(
                    "WEBSOCKET FOUND:",
                    websocket
                )



                if websocket:

                    conv_id = data.get("conversation_id")
                    try:

                        await websocket.send_json({

                            "type": "start",
                            "conversation_id": conv_id
                        })

                        await websocket.send_json({

                            "type": "chunk",
                            "conversation_id": conv_id,
                            "content":
                                data.get(
                                    "response",
                                    ""
                                )
                        })

                        await websocket.send_json({

                            "type": "done",
                            "conversation_id": conv_id
                        })

                    except Exception as e:

                        print(
                            f"WebSocket send failed: {e}"
                        )

                await redis_client.xack(

                    CHAT_RESPONSE_STREAM,

                    GROUP_NAME,

                    message_id,
                )


asyncio.run(
    process_events()
)

