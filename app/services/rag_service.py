from pypdf import PdfReader
import os

from sqlalchemy.orm import Session

from app.services.vector_service import (
    store_document,
    semantic_search
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
    pdf_path: str
):

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

    return {
        "status": "success",
        "chunks_stored": total_chunks
    }


# -----------------------------
# BUILD RAG CONTEXT
# -----------------------------

def retrieve_context(
    db: Session,
    query: str,
    top_k: int = 3
):

    results = semantic_search(
        db=db,
        query=query,
        limit=top_k
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