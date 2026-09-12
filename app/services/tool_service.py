import logging
from sqlalchemy import select, func
from app.models.document_job import DocumentJob
from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase
from app.services.vector_service import semantic_search

logger = logging.getLogger("tool_service")


async def get_system_stats(db):
    try:
        # Check if db is async session
        if hasattr(db, "execute"):
            total_jobs = (await db.execute(select(func.count(DocumentJob.id)))).scalar() or 0
            completed_jobs = (await db.execute(select(func.count(DocumentJob.id)).filter(DocumentJob.status == "completed"))).scalar() or 0
            failed_jobs = (await db.execute(select(func.count(DocumentJob.id)).filter(DocumentJob.status == "failed"))).scalar() or 0
            total_docs = (await db.execute(select(func.count(Document.id)))).scalar() or 0
        else:
            total_jobs = db.query(DocumentJob).count()
            completed_jobs = db.query(DocumentJob).filter(DocumentJob.status == "completed").count()
            failed_jobs = db.query(DocumentJob).filter(DocumentJob.status == "failed").count()
            total_docs = db.query(Document).count()

        return {
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "total_documents": total_docs
        }
    except Exception as e:
        logger.warning(f"get_system_stats error: {e}")
        return {
            "total_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "total_documents": 0
        }


async def search_documents_tool(
    db,
    query: str,
    user_department: str,
    user_role: str
):
    try:
        # Fetch active knowledge bases
        if hasattr(db, "execute"):
            kb_res = await db.execute(select(KnowledgeBase.id).filter(KnowledgeBase.is_active == True))
            kb_ids = [row[0] for row in kb_res.fetchall()]
        else:
            kb_ids = [kb.id for kb in db.query(KnowledgeBase.id).filter(KnowledgeBase.is_active == True).all()]

        if not kb_ids:
            return []

        results = await semantic_search(
            db=db,
            query=query,
            knowledge_base_ids=kb_ids,
            user_department=user_department,
            user_role=user_role,
            limit=10
        )

        formatted = []
        for r in results:
            content = getattr(r, "content", "") if hasattr(r, "content") else str(r)
            source_file = getattr(r, "source_file", None)
            page_number = getattr(r, "page_number", None)
            formatted.append({
                "content": content[:300] if content else "",
                "source_file": source_file,
                "page_number": page_number
            })

        return formatted
    except Exception as e:
        logger.warning(f"search_documents_tool error: {e}")
        return []