import json
import uuid

from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.job_service import (
    create_job
)

from app.db.redis_client import (
    redis_client
)

from app.shared.constants.streams import (
    INGESTION_STREAM
)

from app.modules.knowledge_bases.services.knowledge_base_document_service import (
    knowledge_base_document_service
)




class KnowledgeBaseUploadService:

    UPLOAD_DIR = (
        Path("storage")
        / "knowledge_bases"
    )

    async def upload_document(
        self,
        db: AsyncSession,
        knowledge_base_id: int,
        file: UploadFile
    ):

        # -----------------------------
        # ENSURE DIRECTORY EXISTS
        # -----------------------------

        self.UPLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        # -----------------------------
        # GENERATE UNIQUE FILE NAME
        # -----------------------------

        file_extension = (
            Path(file.filename).suffix
        )

        unique_filename = (
            f"{uuid.uuid4()}"
            f"{file_extension}"
        )

        file_path = (
            self.UPLOAD_DIR
            / unique_filename
        )

        # -----------------------------
        # SAVE FILE
        # -----------------------------

        content = await file.read()

        with open(
            file_path,
            "wb"
        ) as buffer:

            buffer.write(
                content
            )

        # -----------------------------
        # CREATE KNOWLEDGE BASE DOCUMENT
        # -----------------------------

        document = await (
            knowledge_base_document_service
            .create_document(
                db=db,
                knowledge_base_id=knowledge_base_id,
                file_name=file.filename,
                file_path=str(file_path),
                mime_type=file.content_type,
                file_size=len(content)
            )
        )

        # -----------------------------
        # CREATE DOCUMENT JOB
        # -----------------------------

        job = await create_job(
            db=db,
            filename=file.filename,
            knowledge_base_document_id=document.id
        )

        # -----------------------------
        # COMMIT TRANSACTION
        # -----------------------------

        await db.commit()

        try:

            await redis_client.xadd(

                INGESTION_STREAM,

                {
                    "data": json.dumps(
                    {
                        "file_path": str(file_path),
                        "job_id": job.id,
                        "knowledge_base_document_id":
                            document.id
                   }
                )
            }
        )

        except Exception:

        # Later:
        # update document/job status

            raise
        # -----------------------------
        # RETURN RESPONSE
        # -----------------------------

        return {
            "document_id": document.id,
            "job_id": job.id,
            "file_name": document.file_name,
            "status": document.status
        }


knowledge_base_upload_service = (
    KnowledgeBaseUploadService()
)