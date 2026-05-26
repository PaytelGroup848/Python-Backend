import asyncio
import json

from app.shared.redis.stream_service import (
    redis_stream_service
)

from app.shared.redis.client import (
    redis_client
)

from app.shared.constants.streams import (
    RAG_STREAM
)

from app.services.rag_service import (
    retrieve_context
)

from app.db.database import (
    AsyncSessionLocal
)


GROUP_NAME = (
    "rag_workers"
)

CONSUMER_NAME = (
    "rag_worker_1"
)


async def process_events():

    print(
        "RAG worker started"
    )

    while True:

        response = (
            await redis_stream_service.consume(

                RAG_STREAM,

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

                query = data["query"]

                async with AsyncSessionLocal() as db:

                    rag_result = (
                        await retrieve_context(

                            db=db,

                            query=query,

                            user_department="general",

                            user_role="employee",

                            top_k=3,
                        )
                    )

                context = (
                    rag_result["context"]
                )

                sources = (
                    rag_result["sources"]
                )

                print(
                    f"Retrieved context "
                    f"for query: {query}"
                )

                await redis_stream_service.publish(

                    "rag_results",

                    {
                        "request_id":
                            data["request_id"],

                        "conversation_id":
                            data["conversation_id"],

                        "context": context,

                        "sources": json.dumps(
                            sources
                        ),
                    },
                )

                await redis_client.xack(

                    RAG_STREAM,

                    GROUP_NAME,

                    message_id,
                )


asyncio.run(
    process_events()
)