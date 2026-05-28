
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




from app.db.database import AsyncSessionLocal

from app.services.job_service import (
    create_job
)

from app.models.document_job import DocumentJob
from app.services.document_parser_service import (
    parse_document
)



from app.core.security import verify_token

logger = logging.getLogger(__name__)


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
    ".jpeg"
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

        # Create ingestion job
        job = await create_job(
            db=db,
            filename=file.filename
        )

        # Background ingestion
        background_tasks.add_task(
            parse_document,
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