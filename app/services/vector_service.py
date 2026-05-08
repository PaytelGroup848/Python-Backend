from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.document import Document
from app.services.embedding_service import generate_embedding

def store_document(
    db: Session,
    content: str
):

    embedding = generate_embedding(content)

    doc = Document(
        content=content,
        embedding=embedding
    )

    db.add(doc)

    db.commit()

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
            embedding <=> CAST(:embedding AS vector)
            AS distance

        FROM documents

        ORDER BY embedding <=> CAST(:embedding AS vector)

        LIMIT :limit
    """)

    results = db.execute(
        sql,
        {
            "embedding": str(embedding),
            "limit": limit
        }
    )

    return results.fetchall()