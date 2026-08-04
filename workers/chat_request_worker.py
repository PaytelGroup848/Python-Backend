
import asyncio
import json
import logging

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




logger = logging.getLogger(__name__)


GROUP_NAME = (
    "chat_workers"
)

CONSUMER_NAME = (
    "chat_worker_1"
)


async def process_chat_requests():

    logger.info(
        "Chat request worker started"
    )

    while True:

        try:

            events = await (
                redis_stream_service.consume(

                    CHAT_REQUEST_STREAM,

                    GROUP_NAME,

                    CONSUMER_NAME,
                )
            )

            if not events:

                await asyncio.sleep(
                    0.1
                )

                continue

            for stream in events:

                messages = stream[1]

                for message in messages:

                    message_id = message[0]

                    payload = message[1]

                    try:

                        data = json.loads(
                            payload["data"]
                        )

                        logger.info(
                            f"Received chat request: {data}"
                        )

                        request_id = (
                            data.get(
                                "request_id"
                            )
                        )

                        user_id = str(
                            data.get(
                                "user_id"
                            )
                        )

                        query = (

                            data.get("query")

                            or

                            data.get("message")
                        )

                        conversation_id = (
                            data.get(
                                "conversation_id"
                            )
                        )

                        assistant_id = data.get("assistant_id")


                        if not query:

                            raise ValueError(
                                "Query is required"
                            )

                        # =========================
                        # RUN AGENT
                        # =========================

                        response = await run_agent(

                            query=query,

                            session_id=str(
                                conversation_id
                            ),

                            user_id=int(
                                user_id
                            ),

                            assistant_id=(
                                int(assistant_id)
                                if assistant_id is not None
                                else None
                            ),

                            user_role="employee",

                            user_department="general",
                        )

                        # =========================
                        # NORMALIZE RESPONSE
                        # =========================

                        response_text = (

                            response["response"]

                            if isinstance(
                                response,
                                dict
                            )

                            else str(response)
                        )

                        logger.info(
                            f"Generated response for user={user_id}"
                        )

                        # =========================
                        # PUBLISH RESPONSE EVENT
                        # =========================

                        
                        await redis_stream_service.publish(

                            CHAT_RESPONSE_STREAM,

                            {

                                "request_id":
                                    request_id,

                                "type":
                                    "message",

                                "response":
                                    response_text,
                            }
                        )





                    except Exception as e:

                        logger.exception(
                            "Chat request processing failed"
                        )

                        try:

                            
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



                        except Exception:

                            logger.exception(
                                "Failed to publish error response"
                            )

                    finally:

                        try:

                            await redis_client.xack(

                                CHAT_REQUEST_STREAM,

                                GROUP_NAME,

                                message_id,
                            )

                        except Exception:

                            logger.exception(
                                "Redis ACK failed"
                            )

        except Exception:

            logger.exception(
                "Worker loop failed"
            )

            await asyncio.sleep(1)


if __name__ == "__main__":

    asyncio.run(
        process_chat_requests()
    )

