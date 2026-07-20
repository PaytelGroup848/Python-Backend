from sqlalchemy.orm import Session

from app.models.document_job import DocumentJob
from app.models.document import Document
from app.services.vector_service import (
    semantic_search
)


def get_system_stats(
    db: Session
):

    total_jobs = db.query(
        DocumentJob
    ).count()

    completed_jobs = db.query(
        DocumentJob
    ).filter(
        DocumentJob.status == "completed"
    ).count()

    failed_jobs = db.query(
        DocumentJob
    ).filter(
        DocumentJob.status == "failed"
    ).count()

    total_documents = db.query(
        Document
    ).count()

    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "total_documents": total_documents
    }

def search_documents_tool(
    db: Session,
    query: str,
    user_department: str,
    user_role: str
):

    results = semantic_search(
        db=db,
        query=query,
        user_department=user_department,
        user_role=user_role,
        limit=10
    )

    formatted = []

    for r in results:

        formatted.append({
            "content": r.content[:300],
            "source_file": r.source_file,
            "page_number": r.page_number
        })

    return formatted