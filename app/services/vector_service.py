from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.document import Document
from app.services.embedding_service import generate_embedding

def store_document(
    db: Session,
    content: str,
    source_file: str = None,
    page_number: int = None
):

    embedding = generate_embedding(content)

    doc = Document(
        content=content,
        embedding=embedding,
        source_file=source_file,
        page_number=page_number
    )
    db.add(doc)

    db.commit()

    db.refresh(doc)

    return doc


def semantic_search(
    db: Session,
    query: str,
    limit: int = 5
):

    embedding = generate_embedding(query)

    sql = text("""
        SELECT
            id,
            content,
            source_file,
            page_number,
            embedding <=> CAST(:embedding AS vector)
            AS distance

        FROM documents

        WHERE
           content ILIKE :keyword

        ORDER BY embedding <=> CAST(:embedding AS vector)

        LIMIT :limit
    """)

    results = db.execute(
        sql,
        {
            "embedding": str(embedding),
            "keyword": f"%{query}%",
            "limit": limit
        }
    )

    return results.fetchall()