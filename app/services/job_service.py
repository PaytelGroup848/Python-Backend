from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_job import DocumentJob


# -----------------------------
# CREATE JOB
# -----------------------------
async def create_job(
    db: AsyncSession,
    filename: str,
    knowledge_base_document_id: int
):

    job = DocumentJob(
        filename=filename,
        
        knowledge_base_document_id=knowledge_base_document_id,
        status="processing"
    )

    db.add(job)

    await db.flush()

    await db.refresh(job)

    return job


# -----------------------------
# COMPLETE JOB
# -----------------------------
async def complete_job(
    db: AsyncSession,
    job_id: int,
    chunks_stored: int
):

    result = await db.execute(
        select(DocumentJob).where(
            DocumentJob.id == job_id
        )
    )

    job = result.scalar_one_or_none()

    if job:

        job.status = "completed"

        job.chunks_stored = chunks_stored

        job.completed_at = datetime.utcnow()

        await db.commit()


# -----------------------------
# FAIL JOB
# -----------------------------
async def fail_job(
    db: AsyncSession,
    job_id: int,
    error: str
):

    result = await db.execute(
        select(DocumentJob).where(
            DocumentJob.id == job_id
        )
    )

    job = result.scalar_one_or_none()

    if job:

        job.status = "failed"

        job.error_message = error

        await db.commit()