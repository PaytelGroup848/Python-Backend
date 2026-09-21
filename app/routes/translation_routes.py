import os
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
    status
)
from fastapi.responses import FileResponse

from app.core.security import verify_token
from app.db.redis_client import redis_client
from app.schemas.translation_studio import (
    TextTranslationRequest,
    TextTranslationResponse,
    DocumentJobCreationResponse,
    DocumentJobStatusResponse,
    SupportedLanguagesResponse,
    DocumentBlock
)
from app.services.document_translation_service import (
    DocumentTranslationService,
    CANONICAL_LANGUAGES,
    TRANSLATION_STORAGE_BASE
)

logger = logging.getLogger(__name__)

router = APIRouter()
translation_service = DocumentTranslationService()

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}


async def _save_and_validate_upload(file: UploadFile) -> str:
    """
    Validates file extension, streamed 25MB size limit, and magic bytes.
    Saves to a temporary path and returns the path.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    temp_dir = os.path.join(TRANSLATION_STORAGE_BASE, "tmp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"upload_{uuid.uuid4().hex}{ext}")

    total_bytes = 0
    header_bytes = bytearray()

    try:
        with open(temp_path, "wb") as f:
            while chunk := await file.read(64 * 1024):  # 64 KB chunks
                total_bytes += len(chunk)
                if total_bytes > MAX_FILE_SIZE_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File exceeds maximum allowed limit of 25MB"
                    )
                if len(header_bytes) < 1024:
                    header_bytes.extend(chunk[:1024 - len(header_bytes)])
                f.write(chunk)
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise

    # Magic byte MIME verification
    if ext == ".pdf":
        if not bytes(header_bytes).startswith(b"%PDF-"):
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise HTTPException(status_code=400, detail="Invalid PDF file: Missing %PDF- signature")
    elif ext in [".docx", ".doc"]:
        if not bytes(header_bytes).startswith(b"PK\x03\x04"):
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise HTTPException(status_code=400, detail="Invalid DOCX file: Missing PK archive signature")
    elif ext == ".txt":
        try:
            bytes(header_bytes).decode("utf-8")
        except UnicodeDecodeError:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise HTTPException(status_code=400, detail="Invalid text file: Non-UTF8 or binary content detected")

    return temp_path


async def _run_translation_job(
    job_id: str,
    temp_file_path: str,
    filename: str,
    owner_id: int,
    source_language: str,
    target_language: str
):
    """
    Background worker that runs the structured document translation pipeline
    and continuously updates Redis state with measurable progress.
    """
    redis_key = f"translation_job:{job_id}"
    user_job_dir = os.path.join(TRANSLATION_STORAGE_BASE, str(owner_id), job_id)
    os.makedirs(user_job_dir, exist_ok=True)

    pdf_out_path = os.path.join(user_job_dir, "translated.pdf")
    docx_out_path = os.path.join(user_job_dir, "translated.docx")

    try:
        # Milestone 1: Parsing
        raw_state = await redis_client.get(redis_key)
        state = json.loads(raw_state) if raw_state else {}
        state.update({
            "status": "parsing",
            "progress_percent": 15,
            "last_heartbeat_at": datetime.now(timezone.utc).isoformat()
        })
        await redis_client.set(redis_key, json.dumps(state), ex=86400)

        # Extract structured blocks
        blocks = translation_service.extract_document(temp_file_path, filename)
        if not blocks:
            raise ValueError("Document appears to be empty or contains no extractable text.")

        chunks = translation_service.chunk_blocks(blocks, max_chars_per_chunk=3500)
        total_chunks = len(chunks)

        state.update({
            "status": "translating",
            "progress_percent": 20,
            "blocks_total": len(blocks),
            "original_blocks": [b.model_dump() for b in blocks],
            "last_heartbeat_at": datetime.now(timezone.utc).isoformat()
        })
        await redis_client.set(redis_key, json.dumps(state), ex=86400)

        # Milestone 2: Translating chunks with measurable progress
        translated_blocks = []
        total_prompt_tokens = 0
        total_completion_tokens = 0

        for chunk_idx, chunk in enumerate(chunks):
            chunk_result = await translation_service.translate_chunk(
                chunk=chunk,
                target_language=target_language,
                source_language=source_language
            )
            translated_blocks.extend(chunk_result["blocks"])
            total_prompt_tokens += chunk_result["prompt_tokens"]
            total_completion_tokens += chunk_result["completion_tokens"]

            # Measurable progress calculation (20% to 90%)
            progress = 20 + int(70 * ((chunk_idx + 1) / total_chunks))
            state.update({
                "progress_percent": min(progress, 90),
                "blocks_completed": len(translated_blocks),
                "prompt_tokens_used": total_prompt_tokens,
                "completion_tokens_used": total_completion_tokens,
                "total_tokens_used": total_prompt_tokens + total_completion_tokens,
                "last_heartbeat_at": datetime.now(timezone.utc).isoformat()
            })
            await redis_client.set(redis_key, json.dumps(state), ex=86400)

        # Milestone 3: Exporting artifacts
        state.update({
            "status": "exporting",
            "progress_percent": 92,
            "translated_blocks": [b.model_dump() for b in translated_blocks],
            "last_heartbeat_at": datetime.now(timezone.utc).isoformat()
        })
        await redis_client.set(redis_key, json.dumps(state), ex=86400)

        translation_service.export_to_docx(translated_blocks, docx_out_path)
        translation_service.export_to_pdf(translated_blocks, pdf_out_path)

        # Milestone 4: Completed
        state.update({
            "status": "completed",
            "progress_percent": 100,
            "available_downloads": ["pdf", "docx"],
            "artifacts": {
                "pdf": pdf_out_path,
                "docx": docx_out_path
            },
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "last_heartbeat_at": datetime.now(timezone.utc).isoformat()
        })
        await redis_client.set(redis_key, json.dumps(state), ex=86400)
        logger.info(f"Translation job {job_id} successfully completed.")

    except Exception as exc:
        logger.exception(f"Translation job {job_id} failed: {exc}")
        raw_state = await redis_client.get(redis_key)
        state = json.loads(raw_state) if raw_state else {}
        state.update({
            "status": "failed",
            "error_message": str(exc),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "last_heartbeat_at": datetime.now(timezone.utc).isoformat()
        })
        await redis_client.set(redis_key, json.dumps(state), ex=86400)

    finally:
        # Prune temporary uploaded raw file
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/languages", response_model=SupportedLanguagesResponse)
async def get_languages():
    """Returns canonical supported languages hosted by the backend."""
    return SupportedLanguagesResponse(languages=CANONICAL_LANGUAGES)


@router.post("/text", response_model=TextTranslationResponse)
async def translate_text(
    req: TextTranslationRequest,
    user=Depends(verify_token)
):
    """Synchronous translation for fast short snippets and paragraphs."""
    result = await translation_service.translate_text_snippet(
        text=req.text,
        target_language=req.target_language,
        source_language=req.source_language or "auto"
    )
    return TextTranslationResponse(
        status="completed",
        source_language=req.source_language or "auto",
        target_language=req.target_language,
        original_text=req.text,
        translated_text=result["translated_text"],
        prompt_tokens=result["prompt_tokens"],
        completion_tokens=result["completion_tokens"],
        total_tokens=result["total_tokens"]
    )


@router.post("/document", response_model=DocumentJobCreationResponse)
async def create_document_translation_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_language: str = Form(...),
    source_language: str = Form("auto"),
    user=Depends(verify_token)
):
    """
    Asynchronous document translation entry point.
    Enforces 25MB streaming limit and magic byte checks, creates a job record in Redis,
    and returns immediately with job_id.
    """
    temp_path = await _save_and_validate_upload(file)
    job_id = uuid.uuid4().hex

    initial_state = {
        "job_id": job_id,
        "owner_id": user["user_id"],
        "filename": file.filename,
        "source_language": source_language,
        "target_language": target_language,
        "status": "queued",
        "progress_percent": 0,
        "blocks_total": 0,
        "blocks_completed": 0,
        "prompt_tokens_used": 0,
        "completion_tokens_used": 0,
        "total_tokens_used": 0,
        "error_message": None,
        "available_downloads": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_heartbeat_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None
    }

    # Store in Redis with 24-hour TTL
    await redis_client.set(f"translation_job:{job_id}", json.dumps(initial_state), ex=86400)

    # Dispatch to background task
    background_tasks.add_task(
        _run_translation_job,
        job_id=job_id,
        temp_file_path=temp_path,
        filename=file.filename,
        owner_id=user["user_id"],
        source_language=source_language,
        target_language=target_language
    )

    return DocumentJobCreationResponse(
        job_id=job_id,
        filename=file.filename,
        status="queued",
        source_language=source_language,
        target_language=target_language,
        message="Document translation job queued successfully"
    )


@router.get("/jobs/{job_id}", response_model=DocumentJobStatusResponse)
async def get_job_status(
    job_id: str,
    user=Depends(verify_token)
):
    """
    Pollable status endpoint.
    Guarantees user ownership and implements stale job crash recovery.
    """
    raw_state = await redis_client.get(f"translation_job:{job_id}")
    if not raw_state:
        raise HTTPException(status_code=404, detail="Translation job not found or expired")

    state = json.loads(raw_state)

    # Ownership check
    if state.get("owner_id") != user["user_id"]:
        raise HTTPException(status_code=403, detail="Access forbidden: You do not own this job")

    # Worker crash recovery: if job is in-flight but last heartbeat was > 5 minutes ago
    current_status = state.get("status")
    last_hb_str = state.get("last_heartbeat_at")
    if current_status in ["parsing", "translating", "exporting"] and last_hb_str:
        try:
            clean_str = last_hb_str.replace("Z", "+00:00")
            last_hb = datetime.fromisoformat(clean_str)
            if last_hb.tzinfo is None:
                last_hb = last_hb.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            if (now - last_hb).total_seconds() > 300:
                state["status"] = "failed"
                state["error_message"] = "Worker timeout or interrupted process. Please retry the upload."
                state["completed_at"] = now.isoformat()
                await redis_client.set(f"translation_job:{job_id}", json.dumps(state), ex=86400)
        except Exception:
            pass

    return DocumentJobStatusResponse(
        job_id=state["job_id"],
        filename=state["filename"],
        status=state["status"],
        progress_percent=state.get("progress_percent", 0),
        source_language=state.get("source_language", "auto"),
        target_language=state.get("target_language", "hi"),
        blocks_total=state.get("blocks_total", 0),
        blocks_completed=state.get("blocks_completed", 0),
        original_blocks=[DocumentBlock(**b) for b in state.get("original_blocks", [])] if state.get("original_blocks") else None,
        translated_blocks=[DocumentBlock(**b) for b in state.get("translated_blocks", [])] if state.get("translated_blocks") else None,
        prompt_tokens_used=state.get("prompt_tokens_used", 0),
        completion_tokens_used=state.get("completion_tokens_used", 0),
        total_tokens_used=state.get("total_tokens_used", 0),
        error_message=state.get("error_message"),
        available_downloads=state.get("available_downloads", []),
        created_at=state.get("created_at"),
        completed_at=state.get("completed_at")
    )


@router.get("/download/{file_type}/{job_id}")
async def download_translated_artifact(
    file_type: str,
    job_id: str,
    user=Depends(verify_token)
):
    """
    IDOR-protected and canonical-path-hardened download streaming endpoint.
    """
    if file_type not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Supported: 'pdf', 'docx'")

    raw_state = await redis_client.get(f"translation_job:{job_id}")
    if not raw_state:
        raise HTTPException(status_code=404, detail="File expired or translation job not found")

    state = json.loads(raw_state)

    # 1. IDOR Guard: User ownership check
    if state.get("owner_id") != user["user_id"]:
        raise HTTPException(status_code=403, detail="Access forbidden: You do not own this document")

    if state.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Translation job is not completed yet")

    artifact_path = state.get("artifacts", {}).get(file_type)
    if not artifact_path:
        raise HTTPException(status_code=404, detail="Requested file format not found in job artifacts")

    # 2. Canonical path traversal defense
    canonical_artifact = os.path.realpath(artifact_path)
    canonical_root = os.path.realpath(TRANSLATION_STORAGE_BASE)

    if not canonical_artifact.startswith(canonical_root + os.sep):
        logger.error(f"Security Alert: Path traversal attempt detected for job {job_id}: {artifact_path}")
        raise HTTPException(status_code=403, detail="Invalid artifact location")

    if not os.path.exists(canonical_artifact):
        raise HTTPException(status_code=404, detail="Artifact file missing from storage disk")

    # Clean download filename
    orig_base = os.path.splitext(state.get("filename", "document"))[0]
    target_lang = state.get("target_language", "translated")
    download_name = f"{orig_base}_{target_lang}.{file_type}"

    media_type = "application/pdf" if file_type == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return FileResponse(
        path=canonical_artifact,
        media_type=media_type,
        filename=download_name
    )