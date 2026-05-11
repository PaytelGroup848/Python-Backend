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

    vector_sql = text("""
        SELECT
            id,
            content,
            source_file,
            page_number,
            embedding <=> CAST(:embedding AS vector)
            AS distance

        FROM documents

        ORDER BY embedding <=> CAST(:embedding AS vector)

        LIMIT :limit
    """)

    keyword_sql = text("""
        SELECT
            id,
            content,
            source_file,
            page_number,
            0.0 AS distance

        FROM documents

        WHERE content ILIKE :keyword

        LIMIT :limit
    """)

    vector_results = db.execute(
        vector_sql,
        {
            "embedding": str(embedding),
            "limit": limit
        }
    ).fetchall()

    keyword_results = db.execute(
        keyword_sql,
        {
            "keyword": f"%{query}%",
            "limit": limit
        }
    ).fetchall()

    combined = {}

    for r in vector_results:

        combined[r.id] = r

    for r in keyword_results:

        combined[r.id] = r

    print("VECTOR RESULTS:", len(vector_results))
    print("KEYWORD RESULTS:", len(keyword_results))
    print("COMBINED RESULTS:", len(combined))    

    return list(combined.values())