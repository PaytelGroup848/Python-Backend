import asyncio
import json
import logging
import uuid

from app.db.redis_client import (
    redis_client
)

from app.db.database import (
    AsyncSessionLocal
)

from app.shared.constants.streams import (
    EMBEDDING_STREAM
)

from app.core.config import (
    EMBEDDING_WORKER_BATCH_SIZE
)

from app.modules.retrieval_runtime.services.embedding_service import (
    generate_embedding,
)

from app.services.vector_service import (
    store_document
)
from app.shared.metrics.metrics_service import (
    metrics_service
)

logger = logging.getLogger(__name__)

WORKER_ID = (
    f"embedding_worker_"
    f"{uuid.uuid4().hex[:8]}"
)

async def ensure_consumer_group():

    try:

        await redis_client.xgroup_create(

            EMBEDDING_STREAM,

            "embedding_group",

            id="0",

            mkstream=True,
        )

    except Exception:

        pass


async def process_embedding_jobs():
    await ensure_consumer_group()
    logger.info(
        f"Embedding worker started: "
        f"{WORKER_ID}"
    )

    while True:
       

        response = await redis_client.xreadgroup(

            groupname="embedding_group",

            consumername=WORKER_ID,

            streams={
                EMBEDDING_STREAM: ">"
            },

            block=5000,

            count=EMBEDDING_WORKER_BATCH_SIZE,
        )

        if not response:
            continue

        for _, messages in response:

            for message_id, data in messages:

                try:

                    payload = json.loads(
                        data[b"data"]
                    )
                    if not payload.get(
                        "knowledge_base_document_id"
                    ):
                        raise ValueError(
                            "Missing knowledge_base_document_id"
                        )

                    if not payload.get(
                        "content"
                    ):
                        raise ValueError(
                            "Missing content"
                        )

                        

                    embedding = await asyncio.wait_for(
                        

                        generate_embedding(
                            payload["content"]
                        ),

                        timeout=60,
                    )

                    async with (
                        AsyncSessionLocal()
                        as db
                    ):

                        await asyncio.wait_for(

                            store_document(
                            db=db,
                            content=payload[
                                "content"
                            ],
                            embedding=embedding,

                            knowledge_base_document_id= 
                            payload[
                                "knowledge_base_document_id"
                            ],
                            source_file=payload.get(
                                "source_file"
                            ),
                            page_number=payload.get(
                                "page_number"
                            ),
                            ),
                            timeout=60,
                         )
                        await db.commit()

                    logger.info(
                        f"Embedding stored: "
                        f"{message_id}"
                    )

                    await redis_client.xack(

                        EMBEDDING_STREAM,

                        "embedding_group",

                        message_id
                    )

                except Exception as e:

                    if "db" in locals():

                        try:
                            await db.rollback()

                        except Exception:
                            pass

                    logger.exception(
                        f"Embedding worker failed: "
                        f"{str(e)}"
                    )

                    try:

                        await redis_client.xack(

                            EMBEDDING_STREAM,

                            "embedding_group",

                            message_id
                        )

                    except Exception:

                        logger.exception(
                            "Failed to acknowledge message"
                  )


if __name__ == "__main__":

    asyncio.run(
        process_embedding_jobs()
    )