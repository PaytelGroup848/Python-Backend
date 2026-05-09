from sqlalchemy.orm import Session
from datetime import datetime

from app.models.document_job import DocumentJob


def create_job(
    db: Session,
    filename: str
):

    job = DocumentJob(
        filename=filename,
        status="processing"
    )

    db.add(job)

    db.commit()

    db.refresh(job)

    return job


def complete_job(
    db: Session,
    job_id: int,
    chunks_stored: int
):

    job = db.query(DocumentJob).filter(
        DocumentJob.id == job_id
    ).first()

    if job:

        job.status = "completed"

        job.chunks_stored = chunks_stored

        job.completed_at = datetime.utcnow()

        db.commit()


def fail_job(
    db: Session,
    job_id: int,
    error: str
):

    job = db.query(DocumentJob).filter(
        DocumentJob.id == job_id
    ).first()

    if job:

        job.status = "failed"

        job.error_message = error

        db.commit()