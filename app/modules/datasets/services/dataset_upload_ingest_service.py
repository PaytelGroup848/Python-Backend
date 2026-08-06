import hashlib

from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy import (
    text,
)

from app.modules.datasets.repositories.dataset_upload_repository import (
    dataset_upload_repository,
)

from app.modules.datasets.services.dataset_storage_service import (
    dataset_storage_service,
)

from app.modules.ingestion.services.parser_execution_service import (
    parser_execution_service,
)

from app.modules.ingestion.services.chunk_execution_service import (
    chunk_execution_service,
)

from app.shared.exceptions.business_exception import (
    BusinessException,
)


class DatasetUploadIngestService:
    """
    Orchestrates parsing an uploaded file into dataset_records.

    Flow:
        1. Resolve the upload from DB
        2. Stream the file bytes from storage
        3. Write bytes to a tmp path
        4. Delegate to the platform's parser registry (PDF, CSV, XLSX, DOCX, TXT …)
        5. Chunk the parsed text (platform chunker registry)
        6. Bulk-insert rows into dataset_records via raw SQL
        7. Update upload.ingestion_status → INGESTED / FAILED
    """

    DEFAULT_CHUNKER_CODE = "RECURSIVE"

    async def ingest(
        self,
        db: AsyncSession,
        upload_id: int,
    ) -> dict:

        upload = await dataset_upload_repository.get_by_id(
            db=db,
            upload_id=upload_id,
        )

        if upload is None:
            raise BusinessException("Dataset upload not found.")

        if upload.ingestion_status == "INGESTED":
            raise BusinessException(
                "This upload has already been ingested."
            )

        # Mark as IN_PROGRESS before work begins
        upload.ingestion_status = "IN_PROGRESS"
        await db.flush()

        try:
            # ── 1. Resolve storage & materialize file to temp path ───────────
            resolved = await dataset_storage_service.resolve_platform_storage(db=db)

            import tempfile, os
            suffix = Path(upload.original_file_name).suffix or ".bin"
            tmp_dir = Path(tempfile.mkdtemp())
            tmp_path = tmp_dir / f"upload_{upload_id}{suffix}"

            await resolved.runtime.materialize(
                storage_reference=upload.storage_reference,
                destination_path=tmp_path,
            )

            try:
                # ── 2. Parse ─────────────────────────────────────────────────
                parsed = await parser_execution_service.execute(
                    file_path=tmp_path,
                    mime_type=upload.mime_type,
                )

                # ── 3. Chunk ─────────────────────────────────────────────────
                chunk_config = {
                    "provider_code": "LOCAL",
                    "tokenizer_code": "GPT2",
                    "nlp_provider_code": "SPACY",
                    "nlp_model_name": "en_core_web_sm",
                    "max_characters": 1000,
                    "overlap_characters": 200,
                }
                chunks = await chunk_execution_service.execute(
                    parsed_document=parsed,
                    chunker_code=self.DEFAULT_CHUNKER_CODE,
                    configuration=chunk_config,
                )

            finally:
                import shutil
                shutil.rmtree(tmp_dir, ignore_errors=True)

            # ── 5. Bulk-insert into dataset_records ──────────────────────────
            inserted = await self._save_chunks(
                db=db,
                dataset_id=upload.dataset_id,
                upload_id=upload.id,
                chunks=chunks,
                source_file=upload.original_file_name,
            )

            # ── 6. Update upload status ──────────────────────────────────────
            upload.ingestion_status = "INGESTED"
            upload.parser_type = parsed.parser_code
            upload.error_message = None
            await db.flush()
            await db.commit()

            return {
                "upload_id": upload_id,
                "ingestion_status": "INGESTED",
                "records_inserted": inserted,
                "parser_used": parsed.parser_code,
            }

        except Exception as exc:
            upload.ingestion_status = "FAILED"
            upload.error_message = str(exc)
            await db.flush()
            await db.commit()
            raise BusinessException(
                f"Ingestion failed: {exc}"
            ) from exc

    # ── helpers ──────────────────────────────────────────────────────────────

    async def _save_chunks(
        self,
        db: AsyncSession,
        dataset_id: int,
        upload_id: int,
        chunks,
        source_file: str,
    ) -> int:
        from datetime import datetime
        import json

        now = datetime.utcnow()
        inserted = 0

        for chunk in chunks:
            text_content = (
                chunk.content
                if hasattr(chunk, "content")
                else str(chunk)
            )

            if not text_content or not text_content.strip():
                continue

            record_hash = hashlib.sha256(
                f"{dataset_id}:{text_content}".encode()
            ).hexdigest()

            meta = json.dumps({
                "source_file": source_file,
                "upload_id": upload_id,
            })

            await db.execute(
                text("""
                    INSERT INTO dataset_records
                        (dataset_id, corpus_source_id, record_type, status,
                         record_hash, input_text, output_text, metadata_json,
                         created_at, updated_at)
                    VALUES
                        (:dataset_id, NULL, 'DOCUMENT_CHUNK', 'ACTIVE',
                         :record_hash, :input_text, NULL,
                         CAST(:metadata_json AS jsonb), :now, :now)
                    ON CONFLICT (dataset_id, record_hash) DO NOTHING
                """),
                {
                    "dataset_id": dataset_id,
                    "record_hash": record_hash,
                    "input_text": text_content.strip(),
                    "metadata_json": meta,
                    "now": now,
                },
            )
            inserted += 1

            if inserted % 200 == 0:
                await db.flush()

        await db.flush()
        return inserted


dataset_upload_ingest_service = DatasetUploadIngestService()
