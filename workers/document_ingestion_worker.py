import asyncio
import json
import logging
import uuid

from app.db.redis_client import (
    redis_client
)

from app.shared.constants.streams import (
    INGESTION_STREAM
)

from app.services.document_ingestion_service import (
    ingest_document_file
)

logger = logging.getLogger(__name__)

WORKER_ID = (
    f"ingestion_worker_"
    f"{uuid.uuid4().hex[:8]}"
)

async def ensure_consumer_group():

    try:

        await redis_client.xgroup_create(

            INGESTION_STREAM,

            "ingestion_group",

            id="0",

            mkstream=True,
        )

    except Exception:

        pass

async def process_ingestion_jobs():

    await ensure_consumer_group()

    logger.info(
        f"Ingestion worker started: "
        f"{WORKER_ID}"
    )

    while True:

        response = await redis_client.xreadgroup(

            groupname="ingestion_group",

            consumername=WORKER_ID,

            streams={
                INGESTION_STREAM: ">"
            },

            block=5000,

            count=10
        )

        if not response:
            continue

        for _, messages in response:

            for message_id, data in messages:

                try:

                    payload = json.loads(
                        data[b"data"].decode()
                    )

                    file_path = payload.get(
                        "file_path"
                    )

                    job_id = payload.get(
                        "job_id"
                    )

                    knowledge_base_document_id = payload.get(
                        "knowledge_base_document_id"
                    )

                    if not file_path:

                        raise ValueError(
                            "Missing file_path"
                        )

                    if not job_id:

                        raise ValueError(
                            "Missing job_id"
                        )

                    if not knowledge_base_document_id:

                        raise ValueError(
                            "Missing knowledge_base_document_id"
                        )

                    await ingest_document_file(

                        file_path=file_path,

                        job_id=job_id,

                        knowledge_base_document_id=
                        knowledge_base_document_id
                    )

                    await redis_client.xack(

                        INGESTION_STREAM,

                        "ingestion_group",

                        message_id
                    )

                    logger.info(
                        f"Ingestion completed: "
                        f"{message_id}"
                    )

                except Exception as e:

                    await redis_client.xack(

                        INGESTION_STREAM,

                        "ingestion_group",

                        message_id
                    )

                    logger.exception(
                        f"Ingestion worker failed: "
                        f"{str(e)}"
                    )
if __name__ == "__main__":

    logger.info(
        "Starting ingestion worker"
    )

    asyncio.run(
        process_ingestion_jobs()
    )
      
