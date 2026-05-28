
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


from app.services.agent_service import (
    run_agent
)



from app.modules.chat.services.queue_service import (
    queue_service
)


GROUP_NAME = "chat_workers"

CONSUMER_NAME = "chat_worker_1"


async def process_chat_requests():

    while True:

        events = await redis_stream_service.consume(

            CHAT_REQUEST_STREAM,

            GROUP_NAME,

            CONSUMER_NAME,
        )

        if not events:
            continue

        for stream in events:

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

                user_id = str(
                    data["user_id"]
                )

                query = (
                    data["query"]
                )

                conversation_id = (
                    data["conversation_id"]
                )

                try:

                    
                    response = await run_agent(

                       query=query,

                       session_id=str(
                           conversation_id
                        ),

                        user_id=int(
                            user_id
                        ),

                        user_role="employee",

                        user_department="general",
                    )



                    await redis_stream_service.publish(

                        CHAT_RESPONSE_STREAM,

                        {
                            "request_id":
                            request_id,

                            "type":
                            "message",

                            "response":
                            response,
                        }
                    )

                except Exception as e:

                    await redis_stream_service.publish(

                        CHAT_RESPONSE_STREAM,

                        {
                            "request_id":
                            request_id,

                            "type":
                            "error",

                            "message":
                            str(e),
                        }
                    )

                finally:

                    await queue_service.decrement(
                        user_id
                    )

                    await redis_client.xack(

                        CHAT_REQUEST_STREAM,

                        GROUP_NAME,

                        message_id,
                    )


asyncio.run(
    process_chat_requests()
)

