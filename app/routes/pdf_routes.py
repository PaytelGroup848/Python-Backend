from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
    BackgroundTasks
)

from sqlalchemy.orm import Session
from app.services.job_service import create_job
from app.models.document_job import DocumentJob

import os

from app.db.database import SessionLocal

from app.services.rag_service import (
    ingest_pdf_file
)

router = APIRouter()

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

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

# -----------------------------
# PDF UPLOAD ROUTE
# -----------------------------

@router.post("/upload-pdf")

async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Validate PDF
    if not file.filename.endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # Save uploaded file
    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    try:

        with open(file_path, "wb") as f:

            content = await file.read()

            f.write(content)

        # Ingest PDF into pgvector
        job = create_job(
           db=db,
           filename=file.filename
        )

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

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
@router.get("/job-status/{job_id}")

def get_job_status(
    job_id: int,
    db: Session = Depends(get_db)
):

    job = db.query(DocumentJob).filter(
        DocumentJob.id == job_id
    ).first()

    if not job:

        return {
            "error": "Job not found"
        }

    return {
        "job_id": job.id,
        "filename": job.filename,
        "status": job.status,
        "chunks_stored": job.chunks_stored,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "completed_at": job.completed_at
    }