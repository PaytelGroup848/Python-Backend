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


@router.post("/documents")

def add_document(
    req: DocumentRequest,
    db: Session = Depends(get_db)
):

    doc = store_document(
        db,
        req.content
    )

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
        req.query
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