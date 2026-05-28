
import logging
import os
import asyncio

import aiofiles

from pypdf import PdfReader

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.core.config import (
    settings
)

from app.services.document_parser_service import (
    parse_document
)

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

from app.services.language_service import (
    detect_language,
    translate_to_english
)


logger = logging.getLogger(__name__)


# -----------------------------
# TEXT CLEANING
# -----------------------------

def clean_text(
    text: str
) -> str:

    if not text:

        return ""

    return (
        text
        .replace("\x00", "")
        .replace("\r", " ")
        .strip()
    )


# -----------------------------
# PUBLISH CHUNKS
# -----------------------------

async def publish_chunks(
    *,
    text: str,
    original_text: str,
    language: str,
    translated: bool,
    source_file: str,
    page_number: int,
    total_chunks: int,
    max_chunks: int
) -> int:

    chunks = chunk_text(text)

    stored = 0

    for chunk in chunks:

        if total_chunks >= max_chunks:

            logger.warning(
                f"Chunk limit exceeded: "
                f"{source_file}"
            )

            break

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
                source_file,

            "page_number":
                page_number,
        })

        stored += 1
        total_chunks += 1

    return stored


# -----------------------------
# PROCESS TEXT PIPELINE
# -----------------------------

async def process_text_pipeline(
    *,
    text: str,
    source_file: str,
    page_number: int,
    total_chunks: int,
    max_chunks: int
) -> int:

    text = clean_text(text)

    if not text:

        return 0

    language = await asyncio.to_thread(

        detect_language,

        text
    )

    original_text = text

    translated = False

    if language != "en":

        logger.info(
            f"Translating page "
            f"{page_number} "
            f"from {language}"
        )

        text = await asyncio.to_thread(

            translate_to_english,

            text
        )

        text = clean_text(text)

        if not text:

            return 0

        translated = True

    stored = await publish_chunks(

        text=text,

        original_text=original_text,

        language=language,

        translated=translated,

        source_file=source_file,

        page_number=page_number,

        total_chunks=total_chunks,

        max_chunks=max_chunks
    )

    return stored


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
            f"File not found: "
            f"{file_path}"
        )

    async with aiofiles.open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        text = await f.read()

    max_chunks = (
        settings.RAG_MAX_INGESTION_CHUNKS
    )

    stored_count = await process_text_pipeline(

        text=text,

        source_file=os.path.basename(
            file_path
        ),

        page_number=1,

        total_chunks=0,

        max_chunks=max_chunks
    )

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
                f"PDF not found: "
                f"{pdf_path}"
            )

        if os.path.getsize(pdf_path) == 0:

            raise ValueError(
                "PDF file is empty"
            )

        reader = await asyncio.to_thread(

            PdfReader,

            pdf_path
        )

        max_chunks = (
            settings.RAG_MAX_INGESTION_CHUNKS
        )

        total_chunks = 0

        ocr_pages_cache = None

        for page_num, page in enumerate(
            reader.pages
        ):

            if total_chunks >= max_chunks:

                break

            try:

                text = await asyncio.to_thread(
                    page.extract_text
                )

            except Exception:

                logger.warning(
                    f"PDF extraction failed: "
                    f"{page_num + 1}"
                )

                continue

            if text:

                text = clean_text(text)

            # -----------------------------
            # OCR FALLBACK
            # -----------------------------

            if not text:

                logger.info(
                    f"OCR fallback triggered "
                    f"for page "
                    f"{page_num + 1}"
                )

                if ocr_pages_cache is None:

                    ocr_pages_cache = (
                        await asyncio.wait_for(

                            extract_text_from_scanned_pdf(
                                pdf_path
                            ),

                            timeout=120,
                        )
                    )

                matching_page = next(

                    (
                        p
                        for p
                        in ocr_pages_cache

                        if p[
                            "page_number"
                        ] == page_num + 1
                    ),

                    None
                )

                if matching_page:

                    text = clean_text(
                        matching_page["text"]
                    )

            if not text:

                continue

            stored = await process_text_pipeline(

                text=text,

                source_file=os.path.basename(
                    pdf_path
                ),

                page_number=(
                    page_num + 1
                ),

                total_chunks=total_chunks,

                max_chunks=max_chunks
            )

            total_chunks += stored

        await complete_job(

            db=db,

            job_id=job_id,

            chunks_stored=total_chunks
        )

        logger.info(
            f"PDF ingestion completed: "
            f"{pdf_path}"
        )

        return {
            "status": "success",
            "chunks_stored": total_chunks
        }

    except Exception as e:

        await db.rollback()

        logger.exception(
            f"PDF ingestion failed: "
            f"{pdf_path}"
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

    if not results:

        return {

            "context": "",

            "sources": [],

            "needs_general_knowledge": True,

            "message": (
                "I could not find "
                "relevant information "
                "in the uploaded "
                "documents."
            )
        }

    results = await rerank_results(
        query,
        results
    )

    results = results[:top_k]

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

    best_result = results[0]

    distance = getattr(

        best_result,

        "distance",

        1.0
    )

    if (
        distance
        >
        settings.RAG_SIMILARITY_THRESHOLD
    ):

        return {

            "context": "",

            "sources": [],

            "needs_general_knowledge": True,

            "message": (
                "I could not find "
                "relevant information "
                "in the uploaded "
                "documents."
            )
        }

    return build_context(
        results
    )


# -----------------------------
# INGEST GENERIC DOCUMENT
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
                f"File not found: "
                f"{file_path}"
            )

        pages = await asyncio.wait_for(

            parse_document(file_path),

            timeout=120,
        )

        max_chunks = (
            settings.RAG_MAX_INGESTION_CHUNKS
        )

        total_chunks = 0

        for page in pages:

            if total_chunks >= max_chunks:

                break

            page_num = page.get(
                "page_number",
                1
            )

            text = clean_text(
                page.get("text", "")
            )

            if not text:

                continue

            stored = await process_text_pipeline(

                text=text,

                source_file=os.path.basename(
                    file_path
                ),

                page_number=page_num,

                total_chunks=total_chunks,

                max_chunks=max_chunks
            )

            total_chunks += stored

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

        logger.exception(
            f"Document ingestion failed: "
            f"{file_path}"
        )

        await fail_job(

            db=db,

            job_id=job_id,

            error=str(e)
        )

        raise
