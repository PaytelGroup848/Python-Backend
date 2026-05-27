import logging
import os
import aiofiles



import asyncio
from pypdf import PdfReader
from app.services.document_ingestion_service import (
    parse_document
)
from sqlalchemy.ext.asyncio import AsyncSession


from app.services.job_service import (
    complete_job,
    fail_job
)

from app.services.vector_service import (
    semantic_search
)
from app.shared.redis.embedding_stream import (
    publish_embedding_job
)

from app.services.ocr_service import (
    extract_text_from_scanned_pdf
)


from app.modules.chat.services.rag.reranking_service import (
    rerank_results
)

from app.modules.chat.services.rag.context_builder import (
    build_context
)

from app.modules.chat.services.rag.chunking_service import (
    chunk_text
)
from app.core.config import (
    RAG_SIMILARITY_THRESHOLD,
    RAG_MAX_INGESTION_CHUNKS
)

from app.services.language_service import (
    detect_language,
    translate_to_english
)


logger = logging.getLogger(__name__)



# -----------------------------
# TEXT CLEANING
# -----------------------------

def clean_text(text: str) -> str:

    return (
        text
        .replace("\x00", "")
        .strip()
    )
   

# -----------------------------
# INGEST TXT FILE
# -----------------------------

async def ingest_text_file(
    file_path: str
) -> dict:

    logger.info(
        f"Starting text ingestion: "
        f"{file_path}"
    )

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )
            
        

    async with aiofiles.open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

       text = await f.read()

    chunks = chunk_text(text)

    stored_count = 0

    for chunk in chunks:

        if chunk.strip():

            await publish_embedding_job({

                "content": chunk,

                "source_file":
                    os.path.basename(
                        file_path
                    ),

                "page_number": 1,
            })

            stored_count += 1
    logger.info(
        f"Text ingestion completed: "
        f"{file_path}"
    )        

    return {
        "status": "success",
        "chunks_stored": stored_count
    }


# -----------------------------
# INGEST PDF FILE
# -----------------------------
async def ingest_pdf_file(
    db: AsyncSession,
    pdf_path: str,
    job_id: int
) -> dict:

    try:

        logger.info(
            f"Starting PDF ingestion: "
            f"{pdf_path}"
        )

        if not os.path.exists(pdf_path):

            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )

        if os.path.getsize(pdf_path) == 0:

            raise ValueError(
                "PDF file is empty"
            )

        reader = await asyncio.to_thread(

            PdfReader,

            pdf_path
        )

        MAX_CHUNKS = RAG_MAX_INGESTION_CHUNKS

        total_chunks = 0

        ocr_pages_cache = None

        for page_num, page in enumerate(reader.pages):

            if total_chunks >= MAX_CHUNKS:
                break

            text = await asyncio.to_thread(

                page.extract_text
             )

            if text:
                text = clean_text(text)

            # -----------------------------
            # OCR FALLBACK
            # -----------------------------

            if not text:

                logger.info(
                    f"OCR fallback triggered for page {page_num + 1}"
                )

                if ocr_pages_cache is None:

                   ocr_pages_cache = await asyncio.wait_for(

                       extract_text_from_scanned_pdf(
                           pdf_path
                       ),

                      timeout=120,
                  )

                matching_page = next(
                    (
                        p for p in ocr_pages_cache
                        if p["page_number"] == page_num + 1
                    ),
                    None
                )

                if matching_page:

                    text = clean_text(
                        matching_page["text"]
                    )

            if not text:
                continue

            # -----------------------------
            # LANGUAGE DETECTION
            # -----------------------------

            language = await asyncio.to_thread(

                detect_language,

                text
            )

            original_text = text

            translated = False

            # -----------------------------
            # TRANSLATE NON-ENGLISH PDFs
            # -----------------------------

            if language != "en":

                logger.info(
                    f"Translating PDF page "
                    f"{page_num + 1} "
                    f"from {language} to English"
                )

                text = await asyncio.to_thread(

                    translate_to_english,

                    text
                )

                translated = True

            chunks = chunk_text(text)

            for chunk in chunks:

                chunk = clean_text(chunk)

                if total_chunks >= MAX_CHUNKS:

                    logger.warning(
                        f"Chunk limit exceeded: {pdf_path}"
                    )

                    break

                if chunk:

                    await publish_embedding_job({

                        "content": chunk,

                        "original_content":
                            original_text,

                        "language":
                            language,

                        "is_translated":
                            translated,

                        "source_file":
                            os.path.basename(
                                pdf_path
                            ),

                       "page_number":
                           page_num + 1,
                    })

                    

                    total_chunks += 1

        await complete_job(
            db=db,
            job_id=job_id,
            chunks_stored=total_chunks
        )

        logger.info(
            f"PDF ingestion completed: {pdf_path}"
        )

        return {
            "status": "success",
            "chunks_stored": total_chunks
        }

    except Exception as e:

        await db.rollback()

        logger.exception(
           f"PDF ingestion failed: {pdf_path}"
        )

        await fail_job(
            db=db,
            job_id=job_id,
            error=str(e)
        )

        raise 

# -----------------------------
# BUILD RAG CONTEXT
# -----------------------------
async def retrieve_context(
    db: AsyncSession,
    query: str,
    user_department: str,
    user_role: str,
    top_k: int = 10
) -> dict:

    if not query.strip():

        return {
            "context": "",
            "sources": []
        }

    results = await asyncio.wait_for(

        semantic_search(

            db=db,

            query=query,

            user_department=
                user_department,

            user_role=
                user_role,

            limit=top_k
        ),

        timeout=30,
    )

    results = await rerank_results(
        query,
        results
    )

    logger.info(
        f"RAG results count: "
        f"{len(results)}"
    )


    for r in results:

        logger.info(
            f"RAG source="
            f"{r.source_file} "
            f"distance="
            f"{getattr(r, 'distance', None)}"
        )

    # -----------------------------
    # NO RESULTS FOUND
    # -----------------------------

    if not results:

        return {
            "context": "",
            "sources": [],
            "needs_general_knowledge": True,
            "message": (
                "I could not find relevant information "
                "in the uploaded documents. "
                "Would you like me to answer using "
                "general AI knowledge?"
            )
        }

    # -----------------------------
    # SIMILARITY VALIDATION
    # -----------------------------

    best_result = results[0]

    distance = getattr(
        best_result,
        "distance",
        1.0
    )

    

    if distance > RAG_SIMILARITY_THRESHOLD:

      

        return {
            "context": "",
            "sources": [],
            "needs_general_knowledge": True,
            "message": (
                "I could not find relevant information "
                "in the uploaded documents. "
                "Would you like me to answer using "
                "general AI knowledge?"
            )
        }
    return build_context(
        results
    )

    # -----------------------------
    # BUILD CONTEXT
    # -----------------------------


async def ingest_document_file(
    db: AsyncSession,
    file_path: str,
    job_id: int
):

    try:

        logger.info(
            f"Starting document ingestion: "
            f"{file_path}"
        )

        if not os.path.exists(file_path):

            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        pages = await asyncio.wait_for(

            parse_document(file_path),

            timeout=120,
        )

        MAX_CHUNKS = RAG_MAX_INGESTION_CHUNKS

        total_chunks = 0

        for page in pages:

            if total_chunks >= MAX_CHUNKS:
                break

            page_num = page["page_number"]

            text = clean_text(
                page["text"]
            )

            if not text:
                continue

            # -----------------------------
            # LANGUAGE DETECTION
            # -----------------------------

            language = await asyncio.to_thread(

                detect_language,

                text
            )

            original_text = text

            translated = False

            # -----------------------------
            # TRANSLATE NON-ENGLISH TEXT
            # -----------------------------

            if language != "en":

                text = await asyncio.to_thread(

                    translate_to_english,

                    text
                )

                translated = True

            chunks = chunk_text(text)

            for chunk in chunks:

                chunk = clean_text(chunk)

                if not chunk:
                    continue

                await publish_embedding_job({

                    "content": chunk,

                    "original_content":
                        original_text,

                    "language":
                        language,

                    "is_translated":
                        translated,

                    "source_file":
                        os.path.basename(
                            file_path
                        ),

                    "page_number":
                        page_num,
                    })

                total_chunks += 1

        await complete_job(
            db=db,
            job_id=job_id,
            chunks_stored=total_chunks
        )

        logger.info(
            f"Document ingestion completed: "
            f"{file_path}"
        )

        return {
            "status": "success",
            "chunks_stored": total_chunks
        }

    except Exception as e:

        await db.rollback()

        await fail_job(
            db=db,
            job_id=job_id,
            error=str(e)
        )

        raise