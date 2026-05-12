from pypdf import PdfReader
import os

from sqlalchemy.orm import Session

from app.services.vector_service import (
    store_document,
    semantic_search
)

from app.services.job_service import (
    complete_job,
    fail_job
)

from sentence_transformers import CrossEncoder
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)
# -----------------------------
# TEXT CLEANING
# -----------------------------

def clean_text(text: str):

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
):

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
    results
):

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

def ingest_text_file(
    db: Session,
    file_path: str
):

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

            store_document(
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
def ingest_pdf_file(
    db: Session,
    pdf_path: str,
    job_id: int
):

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

        total_chunks = 0

        for page_num, page in enumerate(reader.pages):

            text = page.extract_text()

            if text:
                text = clean_text(text)

            if not text:
                continue

            chunks = chunk_text(text)

            for chunk in chunks:

                chunk = clean_text(chunk)

                if chunk:

                    store_document(
                        db=db,
                        content=chunk,
                        source_file=os.path.basename(pdf_path),
                        page_number=page_num + 1
                    )

                    total_chunks += 1

        complete_job(
            db=db,
            job_id=job_id,
            chunks_stored=total_chunks
        )

        return {
            "status": "success",
            "chunks_stored": total_chunks
        }

    except Exception as e:

        fail_job(
            db=db,
            job_id=job_id,
            error=str(e)
        )

        raise e

# -----------------------------
# BUILD RAG CONTEXT
# -----------------------------

def retrieve_context(
    db: Session,
    query: str,
    user_department: str,
    user_role: str,
    top_k: int = 10
):

    results = semantic_search(
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

        

    return {
        "context": "\n\n".join(context_parts),
        "sources": sources
    }