
import os
import uuid
import logging

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
    BackgroundTasks
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession




from datetime import datetime

from app.db.database import AsyncSessionLocal
from app.services.job_service import create_job, complete_job, fail_job
from app.models.document_job import DocumentJob
from app.models.knowledge_base import KnowledgeBase
from app.models.knowledge_base_document import KnowledgeBaseDocument
from app.services.document_parser_service import parse_document
from app.core.security import verify_token

logger = logging.getLogger(__name__)


async def _process_uploaded_document(file_path: str, job_id: int):
    try:
        parsed = await parse_document(file_path)
        chunks_count = len(parsed) if isinstance(parsed, list) else 1
        async with AsyncSessionLocal() as session:
            await complete_job(db=session, job_id=job_id, chunks_stored=chunks_count)
    except Exception as e:
        logger.exception(f"Background parsing failed for job {job_id}: {e}")
        try:
            async with AsyncSessionLocal() as session:
                await fail_job(db=session, job_id=job_id, error=str(e))
        except Exception:
            pass


router = APIRouter(
    prefix="/pdf",
    tags=["PDF Processing"]
)

# -----------------------------
# UPLOAD DIRECTORY
# -----------------------------

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

# -----------------------------
# DATABASE DEPENDENCY
# -----------------------------

async def get_db():

    async with AsyncSessionLocal() as db:

        yield db

# -----------------------------
# SUPPORTED FILE TYPES
# -----------------------------

SUPPORTED_EXTENSIONS = [
    ".pdf",
    ".docx",
    ".txt",
    ".csv",
    ".xlsx",
    ".pptx",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp"
]

# -----------------------------
# DOCUMENT UPLOAD ROUTE
# -----------------------------

@router.post("/upload-pdf")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(verify_token)
):
    
    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension not in SUPPORTED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )

    safe_filename = (
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        safe_filename
    )

    try:

        # Save uploaded file
        with open(file_path, "wb") as f:

            content = await file.read()

            MAX_FILE_SIZE = 20 * 1024 * 1024

            if len(content) > MAX_FILE_SIZE:

                raise HTTPException(
                    status_code=400,
                    detail="File too large"
                )

            f.write(content)

        # Ensure active knowledge base exists
        kb_result = await db.execute(
            select(KnowledgeBase).filter(KnowledgeBase.is_active == True).limit(1)
        )
        kb = kb_result.scalar_one_or_none()

        if not kb:
            kb = KnowledgeBase(
                name="Default Knowledge Base",
                code="DEFAULT_KB",
                description="Default Knowledge Base for document uploads",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(kb)
            await db.flush()
            await db.refresh(kb)

        # Create knowledge base document entry
        kb_doc = KnowledgeBaseDocument(
            knowledge_base_id=kb.id,
            file_name=file.filename,
            file_path=file_path,
            mime_type=file.content_type or "application/pdf",
            file_size=len(content),
            is_active=True,
            status="processing",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(kb_doc)
        await db.flush()
        await db.refresh(kb_doc)

        # Create ingestion job
        job = await create_job(
            db=db,
            filename=file.filename,
            knowledge_base_document_id=kb_doc.id
        )

        await db.commit()

        # Background ingestion
        background_tasks.add_task(
            _process_uploaded_document,
            file_path,
            job.id
        )

        # Store latest uploaded file
        from app.db.redis_client import redis_client

        await redis_client.set(
            f"latest_pdf:{user['user_id']}",
            file.filename
        )
        logger.info(
            f"Document uploaded: {job.id}"
        )

        return {
            "message": "Document uploaded successfully",
            "job_id": job.id,
            "status": "processing",
            "filename": file.filename
        }

    except Exception:

        logger.exception(
            "PDF upload failed"
        )

        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Document upload failed"
        )

# -----------------------------
# JOB STATUS ROUTE
# -----------------------------

@router.get("/job-status/{job_id}")
async def get_job_status(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(DocumentJob).where(
            DocumentJob.id == job_id
        )
    )

    job = result.scalar_one_or_none()

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return {
        "job_id": job.id,
        "filename": job.filename,
        "status": job.status,
        "chunks_stored": job.chunks_stored,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "completed_at": job.completed_at
    }