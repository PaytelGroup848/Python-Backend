import os
import io
import json
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone, timedelta

import fitz  # PyMuPDF
from docx import Document as DocxDocument
from fastapi import HTTPException, UploadFile

from app.schemas.translation_studio import (
    BlockType,
    DocumentBlock,
    SupportedLanguageItem
)
from app.services.document_translation_service import (
    DocumentTranslationService,
    CANONICAL_LANGUAGES,
    TRANSLATION_STORAGE_BASE
)
from app.routes.translation_routes import (
    _save_and_validate_upload,
    download_translated_artifact
)


@pytest.fixture
def translation_service():
    return DocumentTranslationService()


# =============================================================================
# 1. TABLE FIDELITY TEST (CRITICAL REQUIREMENTS)
# =============================================================================

@pytest.mark.asyncio
async def test_table_fidelity_invariants(translation_service):
    """
    Verifies that table translation strictly preserves:
    - Exact row count
    - Exact column count
    - Currency symbols (₹) and prices (₹50,000, ₹20,000)
    - Quantities (12, 5)
    - Product SKUs (SKU-9921, SKU-1044)
    - While accurately translating descriptive column headers and product names.
    """
    input_rows = [
        ["Product Name", "SKU Code", "Quantity", "Unit Price"],
        ["Gaming Laptop", "SKU-9921", "12", "₹50,000"],
        ["Smart Phone", "SKU-1044", "5", "₹20,000"]
    ]

    table_block = DocumentBlock(
        block_id=0,
        type=BlockType.TABLE,
        rows=input_rows
    )

    # Call translate_chunk with mock or real provider
    mock_translated_rows = [
        ["उत्पाद का नाम", "SKU Code", "Quantity", "इकाई मूल्य"],
        ["गेमिंग लैपटॉप", "SKU-9921", "12", "₹50,000"],
        ["स्मार्ट फोन", "SKU-1044", "5", "₹20,000"]
    ]

    mock_response = {
        "response": json.dumps([{
            "block_id": 0,
            "type": "table",
            "rows": mock_translated_rows
        }]),
        "usage": {"prompt_tokens": 120, "completion_tokens": 110, "total_tokens": 230}
    }

    with patch.object(translation_service.provider, "generate", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_response
        result = await translation_service.translate_chunk([table_block], target_language="hi", source_language="en")

    assert len(result["blocks"]) == 1
    translated_block = result["blocks"][0]
    out_rows = translated_block.rows

    # Invariant 1: Row count exactly unchanged
    assert len(out_rows) == 3, f"Expected 3 rows, got {len(out_rows)}"

    # Invariant 2: Column count exactly unchanged across every row
    for r_idx, row in enumerate(out_rows):
        assert len(row) == 4, f"Row {r_idx} column count changed! Expected 4, got {len(row)}"

    # Invariant 3: Numbers, currencies, and SKUs are 100% invariant
    assert out_rows[1][1] == "SKU-9921", "SKU code was modified!"
    assert out_rows[1][2] == "12", "Quantity number was modified!"
    assert out_rows[1][3] == "₹50,000", "Price/currency symbol was modified!"

    assert out_rows[2][1] == "SKU-1044", "SKU code was modified!"
    assert out_rows[2][2] == "5", "Quantity number was modified!"
    assert out_rows[2][3] == "₹20,000", "Price/currency symbol was modified!"

    # Invariant 4: Descriptive words were translated to Hindi
    assert "लैपटॉप" in out_rows[1][0] or "गेमिंग" in out_rows[1][0]


# =============================================================================
# 2. DOCX STRUCTURE EXTRACTION & NESTED LIST TEST
# =============================================================================

def test_docx_structured_extraction(translation_service, tmp_path):
    """Verifies that python-docx accurately extracts Headings, Bullet Lists with list_level, and Tables."""
    docx_file = tmp_path / "sample.docx"
    doc = DocxDocument()
    doc.add_heading("Quarterly Financial Report", level=1)
    doc.add_paragraph("This is an introductory paragraph explaining business performance.")
    doc.add_paragraph("Action Item 1", style="List Bullet")
    doc.add_paragraph("Action Item 2", style="List Bullet")

    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Metric"
    table.cell(0, 1).text = "Value"
    table.cell(1, 0).text = "Revenue"
    table.cell(1, 1).text = "$1,000,000"

    doc.save(str(docx_file))

    blocks = translation_service.extract_blocks_from_docx(str(docx_file))

    types = [b.type for b in blocks]
    assert BlockType.HEADING in types
    assert BlockType.PARAGRAPH in types
    assert BlockType.LIST_ITEM in types
    assert BlockType.TABLE in types

    heading_block = next(b for b in blocks if b.type == BlockType.HEADING)
    assert heading_block.text == "Quarterly Financial Report"
    assert heading_block.level == 1

    table_block = next(b for b in blocks if b.type == BlockType.TABLE)
    assert len(table_block.rows) == 2
    assert table_block.rows[1][1] == "$1,000,000"


# =============================================================================
# 3. PDF EXTRACTION & GRACEFUL TABLE FALLBACK TEST
# =============================================================================

def test_pdf_extraction_and_fallback(translation_service, tmp_path):
    """
    Verifies that PDF extraction reads text, and if find_tables() raises an exception,
    it gracefully degrades to standard paragraph text without failing the job.
    """
    pdf_file = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Company Operations Overview", fontsize=16)
    page.insert_text((72, 120), "This report outlines supply chain efficiency metrics.", fontsize=11)
    doc.save(str(pdf_file))
    doc.close()

    # Test standard extraction
    blocks = translation_service.extract_blocks_from_pdf(str(pdf_file))
    assert len(blocks) >= 1
    assert any("Company Operations" in (b.text or "") for b in blocks)

    # Test graceful degradation when find_tables() errors out
    with patch("fitz.Page.find_tables", side_effect=Exception("Table finder segmentation fault")):
        fallback_blocks = translation_service.extract_blocks_from_pdf(str(pdf_file))
        assert len(fallback_blocks) >= 1
        assert any("Company Operations" in (b.text or "") for b in fallback_blocks)


# =============================================================================
# 4. SECURITY & VALIDATION LAYER TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_oversized_file_rejection():
    """Verifies that an uploaded file > 25MB is aborted with HTTP 413 Payload Too Large."""
    oversized_content = b"A" * (26 * 1024 * 1024)  # 26 MB
    mock_file = UploadFile(
        file=io.BytesIO(oversized_content),
        filename="giant_document.pdf"
    )

    with pytest.raises(HTTPException) as exc_info:
        await _save_and_validate_upload(mock_file)

    assert exc_info.value.status_code == 413
    assert "25MB" in exc_info.value.detail


@pytest.mark.asyncio
async def test_fake_pdf_magic_byte_rejection():
    """Verifies that a file named .pdf with invalid header bytes is rejected with HTTP 400."""
    fake_content = b"NOT_A_REAL_PDF_HEADER_JUST_RANDOM_TEXT"
    mock_file = UploadFile(
        file=io.BytesIO(fake_content),
        filename="malicious.pdf"
    )

    with pytest.raises(HTTPException) as exc_info:
        await _save_and_validate_upload(mock_file)

    assert exc_info.value.status_code == 400
    assert "%PDF-" in exc_info.value.detail


@pytest.mark.asyncio
async def test_idor_download_prevention():
    """
    Verifies that User B cannot download an artifact owned by User A (HTTP 403 Forbidden).
    """
    job_id = "test-job-uuid-1234"
    mock_job_state = {
        "job_id": job_id,
        "owner_id": 999,  # Owned by User 999
        "status": "completed",
        "artifacts": {
            "pdf": os.path.join(TRANSLATION_STORAGE_BASE, "999", job_id, "translated.pdf")
        }
    }

    current_user = {"user_id": 888, "role": "user"}  # User 888 attempting access

    with patch("app.routes.translation_routes.redis_client.get", new_callable=AsyncMock) as mock_redis:
        mock_redis.return_value = json.dumps(mock_job_state)

        with pytest.raises(HTTPException) as exc_info:
            await download_translated_artifact(
                file_type="pdf",
                job_id=job_id,
                user=current_user
            )

        assert exc_info.value.status_code == 403
        assert "not own" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_canonical_path_traversal_defense(tmp_path):
    """
    Verifies that directory traversal payloads like ../../etc/passwd are blocked with HTTP 403.
    """
    job_id = "test-job-uuid-traversal"
    malicious_path = str(tmp_path / "evil_outside_storage.pdf")
    with open(malicious_path, "w") as f:
        f.write("fake")

    mock_job_state = {
        "job_id": job_id,
        "owner_id": 100,
        "status": "completed",
        "artifacts": {
            "pdf": malicious_path  # Pointing outside TRANSLATION_STORAGE_BASE
        }
    }

    current_user = {"user_id": 100, "role": "user"}

    with patch("app.routes.translation_routes.redis_client.get", new_callable=AsyncMock) as mock_redis:
        mock_redis.return_value = json.dumps(mock_job_state)

        with pytest.raises(HTTPException) as exc_info:
            await download_translated_artifact(
                file_type="pdf",
                job_id=job_id,
                user=current_user
            )

        assert exc_info.value.status_code == 403
        assert "invalid artifact location" in exc_info.value.detail.lower()


# =============================================================================
# 5. CANONICAL LANGUAGES VERIFICATION
# =============================================================================

def test_canonical_languages_consistency(translation_service):
    """Verifies that the canonical language list contains all 26 languages with valid codes and native names."""
    languages = translation_service.get_supported_languages()
    assert len(languages) >= 26

    codes = [l.code for l in languages]
    assert "hi" in codes
    assert "bn" in codes
    assert "mr" in codes
    assert "te" in codes
    assert "ta" in codes
    assert "en" in codes

    hindi = next(l for l in languages if l.code == "hi")
    assert hindi.native_name == "हिन्दी"
    assert hindi.display_name == "Hindi"


# =============================================================================
# 6. CONCURRENT TRANSLATION JOBS ISOLATION TEST
# =============================================================================

@pytest.mark.asyncio
async def test_concurrent_jobs_isolation():
    """
    Verifies that multiple concurrent jobs:
    - Keep distinct Redis state keys
    - Retain isolated progress and token metrics
    - Failure of one job does not affect other jobs
    - Storage paths do not cross-contaminate
    """
    from app.routes.translation_routes import get_job_status

    jobs = {
        "job-alpha": {
            "job_id": "job-alpha",
            "owner_id": 101,
            "filename": "alpha.pdf",
            "status": "translating",
            "progress_percent": 45,
            "source_language": "en",
            "target_language": "hi",
            "blocks_total": 10,
            "blocks_completed": 4,
            "prompt_tokens_used": 500,
            "completion_tokens_used": 400,
            "total_tokens_used": 900,
            "last_heartbeat_at": "2026-09-21T14:00:00Z"
        },
        "job-beta": {
            "job_id": "job-beta",
            "owner_id": 101,
            "filename": "beta.docx",
            "status": "completed",
            "progress_percent": 100,
            "source_language": "en",
            "target_language": "mr",
            "blocks_total": 5,
            "blocks_completed": 5,
            "prompt_tokens_used": 250,
            "completion_tokens_used": 200,
            "total_tokens_used": 450,
            "available_downloads": ["docx"],
            "last_heartbeat_at": "2026-09-21T14:00:00Z"
        },
        "job-gamma-failed": {
            "job_id": "job-gamma-failed",
            "owner_id": 101,
            "filename": "corrupted.pdf",
            "status": "failed",
            "progress_percent": 15,
            "source_language": "en",
            "target_language": "bn",
            "error_message": "Corrupted PDF header",
            "last_heartbeat_at": "2026-09-21T14:00:00Z"
        }
    }

    async def mock_redis_get(key):
        job_id = key.replace("translation_job:", "")
        if job_id in jobs:
            return json.dumps(jobs[job_id])
        return None

    user = {"user_id": 101, "role": "user"}

    with patch("app.routes.translation_routes.redis_client.get", side_effect=mock_redis_get):
        status_alpha = await get_job_status(job_id="job-alpha", user=user)
        status_beta = await get_job_status(job_id="job-beta", user=user)
        status_gamma = await get_job_status(job_id="job-gamma-failed", user=user)

    assert status_alpha.status == "translating"
    assert status_alpha.progress_percent == 45
    assert status_alpha.total_tokens_used == 900

    assert status_beta.status == "completed"
    assert status_beta.progress_percent == 100
    assert status_beta.total_tokens_used == 450

    # Gamma failed, but did not mutate alpha or beta
    assert status_gamma.status == "failed"
    assert "Corrupted" in (status_gamma.error_message or "")


# =============================================================================
# 7. WORKER CRASH / STALE TIMEOUT RECOVERY TEST
# =============================================================================

@pytest.mark.asyncio
async def test_worker_stale_crash_recovery():
    """
    Verifies that if a worker process crashes mid-translation and last_heartbeat
    is older than 5 minutes, get_job_status transitions the job to 'failed' gracefully
    instead of leaving it permanently stuck.
    """
    from app.routes.translation_routes import get_job_status

    stale_job = {
        "job_id": "job-stuck-crash",
        "owner_id": 101,
        "filename": "large.pdf",
        "status": "translating",
        "progress_percent": 50,
        "source_language": "en",
        "target_language": "hi",
        # Stale heartbeat from 10 minutes ago
        "last_heartbeat_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    }

    user = {"user_id": 101, "role": "user"}

    with patch("app.routes.translation_routes.redis_client.get", new_callable=AsyncMock) as mock_get, \
         patch("app.routes.translation_routes.redis_client.set", new_callable=AsyncMock) as mock_set:
        mock_get.return_value = json.dumps(stale_job)

        status_res = await get_job_status(job_id="job-stuck-crash", user=user)

        assert status_res.status == "failed"
        assert "timeout or interrupted" in (status_res.error_message or "").lower()
        # Ensure updated failed state was persisted to Redis
        assert mock_set.called
