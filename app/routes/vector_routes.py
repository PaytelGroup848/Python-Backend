from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.services.vector_service import (
    store_document,
    semantic_search
)

router = APIRouter()

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


class DocumentRequest(BaseModel):

    content: str


class SearchRequest(BaseModel):

    query: str
    limit: int = 5


@router.post("/documents")

def add_document(
    req: DocumentRequest,
    db: Session = Depends(get_db)
):

    try:

       doc = store_document(
          db,
          req.content
       )

    except Exception as e:

       return {
          "error": str(e)
       }

    return {
        "message": "stored",
        "id": doc.id
    }


@router.post("/search")

def search(
    req: SearchRequest,
    db: Session = Depends(get_db)
):

    results = semantic_search(
       db,
       req.query,
       req.limit
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