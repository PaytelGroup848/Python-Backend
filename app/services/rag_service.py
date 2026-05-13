import logging
import os
from typing import Sequence
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession
from sentence_transformers import CrossEncoder

from app.services.job_service import (
    complete_job,
    fail_job
)

from app.services.vector_service import (
    semantic_search,
    store_document
)

logger = logging.getLogger(__name__)


reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)
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
# SMART CHUNKING
# -----------------------------

def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> list[str]:

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk.strip())

        start += chunk_size - overlap

    return chunks

def rerank_results(
    query: str,
    results: Sequence
) -> list:

    pairs = [
        (query, r.content)
        for r in results
    ]

    scores = reranker.predict(pairs)

    reranked = sorted(
        zip(results, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [r[0] for r in reranked]


# -----------------------------
# INGEST TXT FILE
# -----------------------------

async def ingest_text_file(
    db: AsyncSession,
    file_path: str
) -> dict:

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        text = f.read()

    chunks = chunk_text(text)

    stored_count = 0

    for chunk in chunks:

        if chunk.strip():

            await store_document(
                db=db,
                content=chunk
            )

            stored_count += 1

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

        if not os.path.exists(pdf_path):

            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )

        if os.path.getsize(pdf_path) == 0:

            raise ValueError(
                "PDF file is empty"
            )

        reader = PdfReader(pdf_path)

        MAX_CHUNKS = 5000

        total_chunks = 0

        for page_num, page in enumerate(reader.pages):

            if total_chunks >= MAX_CHUNKS:
                break

            text = page.extract_text()

            if text:
                text = clean_text(text)

            if not text:
                continue

            chunks = chunk_text(text)

            for chunk in chunks:

                chunk = clean_text(chunk)

                if total_chunks >= MAX_CHUNKS:

                    logger.warning(
                        f"Chunk limit exceeded: {pdf_path}"
                    )

                    break

                if chunk:

                    await store_document(
                        db=db,
                        content=chunk,
                        source_file=os.path.basename(pdf_path),
                        page_number=page_num + 1
                    )

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

    results = await semantic_search(
        db=db,
        query=query,
        user_department=user_department,
        user_role=user_role,
        limit=top_k
     )
    results = rerank_results(
        query,
        results
    )

    if not results:

        return {
            "context": "",
            "sources": []
        }

    context_parts = []

    sources = []

    for r in results:

        context_parts.append(r.content)

        sources.append({
            "source_file": r.source_file,
            "page_number": r.page_number
        })

        

    MAX_CONTEXT_CHARS = 12000

    context = "\n\n".join(context_parts)

    context = context[:MAX_CONTEXT_CHARS]

    return {
        "context": context,
        "sources": sources
    }