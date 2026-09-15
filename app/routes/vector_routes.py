from fastapi import APIRouter, Depends
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

from app.services.vector_service import (
    store_document,
    semantic_search
)

router = APIRouter(
    prefix="/vectors",
    tags=["Vector Search"]
)


# -----------------------------
# REQUEST SCHEMAS
# -----------------------------
class DocumentRequest(BaseModel):

    content: str


class SearchRequest(BaseModel):

    query: str

    limit: int = 5


# -----------------------------
# STORE DOCUMENT
# -----------------------------
@router.post("/documents")
async def add_document(
    req: DocumentRequest,
    db: AsyncSession = Depends(get_db)
):

    try:

        doc = await store_document(
            db=db,
            content=req.content
        )

        return {
            "message": "stored",
            "id": doc.id
        }

    except Exception as e:

        await db.rollback()

        return {
            "error": str(e)
        }


# -----------------------------
# SEMANTIC SEARCH
# -----------------------------
@router.post("/search")
async def search(
    req: SearchRequest,
    db: AsyncSession = Depends(get_db)
):

    results = await semantic_search(
        db=db,
        query=req.query,
        limit=req.limit
    )

    return {
        "results": [
            {
                "id": r.id,
                "content": r.content,
                "distance": r.distance
            }
            for r in results
        ]
    }