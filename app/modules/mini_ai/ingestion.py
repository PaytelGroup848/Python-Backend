import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.mini_ai.schemas import MAX_CHUNKS_PER_MINI_AI, QAPair
from app.modules.retrieval_runtime.services.chunking_service import chunk_text
from app.modules.retrieval_runtime.services.embedding_service import get_embedding_model
from app.services.file_parser_service import (
    parse_csv,
    parse_docx,
    parse_pdf,
    parse_txt,
    parse_xlsx,
)
from app.services.vector_service import store_document

# Cap concurrent CPU embedding operations across all users on CPU VPS.
_EMBEDDING_SEMAPHORE = asyncio.Semaphore(3)


def parse_qa_pairs(qa_json: str | None) -> list[str]:
    if not qa_json or not qa_json.strip():
        return []
    try:
        raw = json.loads(qa_json)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid Q&A JSON format.") from exc

    if not isinstance(raw, list):
        raise ValueError("Q&A payload must be a list of question/answer objects.")

    blocks: list[str] = []
    for item in raw:
        pair = QAPair.model_validate(item)
        blocks.append(f"Question: {pair.question.strip()}\nAnswer: {pair.answer.strip()}")
    return blocks


async def extract_text_from_upload(file_path: str, ext: str) -> str:
    parser_map = {
        ".pdf": parse_pdf,
        ".csv": parse_csv,
        ".txt": parse_txt,
        ".docx": parse_docx,
        ".xlsx": parse_xlsx,
    }
    parser_fn = parser_map.get(ext)
    if parser_fn is None:
        raise ValueError(f"Unsupported file type: {ext}")

    parsed = await asyncio.to_thread(parser_fn, file_path)
    if isinstance(parsed, str):
        return parsed
    if isinstance(parsed, list):
        return "\n\n".join(
            str(page.get("text", "")).strip()
            for page in parsed
            if isinstance(page, dict) and page.get("text")
        )
    return ""


async def index_knowledge_texts(
    db: AsyncSession,
    kbd_id: int,
    source_name: str,
    raw_texts: list[str],
    uploaded_by: int,
    max_chunks: int = MAX_CHUNKS_PER_MINI_AI,
) -> int:
    chunks: list[str] = []
    seen: set[str] = set()
    for text in raw_texts:
        cleaned = (text or "").strip()
        if not cleaned:
            continue
        for piece in chunk_text(cleaned):
            norm = piece.strip()
            if norm and norm not in seen:
                seen.add(norm)
                chunks.append(f"Source: {source_name}\n{norm}")

    if not chunks:
        return 0

    if len(chunks) > max_chunks:
        raise ValueError(
            f"Knowledge exceeds remaining limit of {max_chunks} chunks "
            f"(got {len(chunks)}). Please upload a smaller file."
        )

    async with _EMBEDDING_SEMAPHORE:
        embeddings = await asyncio.to_thread(
            lambda: get_embedding_model().encode(chunks).tolist()
        )

    for chunk, embedding in zip(chunks, embeddings):
        await store_document(
            db=db,
            embedding=embedding,
            content=chunk,
            knowledge_base_document_id=kbd_id,
            source_file=source_name,
            department="personal",
            access_level="private",
            uploaded_by=uploaded_by,
        )

    return len(chunks)
