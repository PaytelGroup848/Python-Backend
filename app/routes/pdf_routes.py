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

import os

from app.db.database import AsyncSessionLocal

from app.services.job_service import (
    create_job
)

from app.models.document_job import DocumentJob

from app.services.rag_service import (
    ingest_pdf_file
)

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

    db = AsyncSessionLocal()

    try:
        yield db

    finally:
        await db.close()

# -----------------------------
# PDF UPLOAD ROUTE
# -----------------------------

@router.post("/upload-pdf")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):

    # Validate PDF
    if not file.filename.endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    try:

        # Save uploaded file
        with open(file_path, "wb") as f:

            content = await file.read()

            f.write(content)

        # Create ingestion job
        job = await create_job(
            db=db,
            filename=file.filename
        )

        # Background ingestion
        background_tasks.add_task(
            ingest_pdf_file,
            db,
            file_path,
            job.id
        )

        return {
            "message": "PDF uploaded successfully",
            "job_id": job.id,
            "status": "processing",
            "filename": file.filename
        }

    except Exception as e:

        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
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