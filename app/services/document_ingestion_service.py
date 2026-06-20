
import json
import logging

from app.db.redis_client import (
    redis_client
)

from app.db.database import (
    AsyncSessionLocal
)

from app.services.document_parser_service import (
    parse_document
)

from app.modules.chat.services.rag.chunking_service import (
    chunk_text
)

from app.services.job_service import (
    update_job_status,
    update_job_chunks
)

from app.shared.constants.streams import (
    EMBEDDING_STREAM,
    INGESTION_STREAM
)


logger = logging.getLogger(__name__)


async def ingest_document_file(
    file_path: str,
    job_id: int,
    knowledge_base_document_id: int
):

    logger.info(
        f"Starting ingestion: "
        f"{file_path}"
    )

    async with AsyncSessionLocal() as db:

        try:

            documents = await parse_document(
                file_path
            )

            total_chunks = 0

            for document in documents:

                text = (
                    document.get("text")
                    or ""
                )

                if not text.strip():

                    continue

                chunks = chunk_text(text)

                total_chunks += len(chunks)

                for chunk in chunks:

                    payload = {
                        "knowledge_base_document_id":
                            knowledge_base_document_id,

                        "content":
                            chunk,

                        "source_file":
                            file_path,

                        "page_number":
                            document.get(
                                "page_number",
                                1
                            )
                        }

                    await redis_client.xadd(

                        EMBEDDING_STREAM,

                        {
                            "data": json.dumps(
                                payload
                            )
                        }
                    )

            await update_job_chunks(
                db=db,
                job_id=job_id,
                chunks_stored=total_chunks
            )

            await update_job_status(
                db=db,
                job_id=job_id,
                status="completed"
            )

            await db.commit()

            logger.info(
                f"Document ingestion completed: "
                f"{file_path}"
            )

        except Exception:

            logger.exception(
                f"Document ingestion failed: "
                f"{file_path}"
            )

            await db.rollback()

            try:

                await update_job_status(
                    db=db,
                    job_id=job_id,
                    status="failed"
                )

                await db.commit()

            except Exception:

                logger.exception(
                    f"Failed to update "
                    f"job status: "
                    f"{job_id}"
                )

            raise