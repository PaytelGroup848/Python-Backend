from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
    BackgroundTasks
)

from sqlalchemy.orm import Session

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
        background_tasks.add_task(
            ingest_pdf_file,
            db,
            file_path
        )

        return {
           "message": "PDF uploaded successfully",
           "status": "processing",
           "filename": file.filename
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )