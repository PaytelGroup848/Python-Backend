"""
BUG-04: Regression Test for Upload Limits & Orphan File Cleanup
"""
import asyncio
import os
import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException

import qa_tests.conftest
from app.routes.pdf_routes import upload_pdf, UPLOAD_DIR


class TestBug04UploadLimits(unittest.TestCase):

    def test_oversized_file_rejected_with_400_and_no_orphan_files(self):
        """Negative test: 21MB payload must return 400 Bad Request, NOT 500, and leave 0 orphan files."""
        async def run_test():
            # Initial count of files in UPLOAD_DIR
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            initial_files = set(os.listdir(UPLOAD_DIR))

            # Simulate 21MB upload
            mock_file = MagicMock()
            mock_file.filename = "oversized_test_doc.pdf"
            mock_file.content_type = "application/pdf"
            # Return 21MB of bytes
            mock_file.read = AsyncMock(return_value=b"X" * (21 * 1024 * 1024))

            mock_bg = MagicMock()
            mock_db = MagicMock()
            mock_db.rollback = AsyncMock()
            mock_user = {"user_id": 1, "role": "employee"}

            with self.assertRaises(HTTPException) as ctx:
                await upload_pdf(background_tasks=mock_bg, file=mock_file, db=mock_db, user=mock_user)

            # Assert correct status code
            self.assertEqual(ctx.exception.status_code, 400, "Oversized file must be rejected with HTTP 400, not 500")
            self.assertIn("File too large", ctx.exception.detail)

            # Assert NO orphan files left in UPLOAD_DIR
            after_files = set(os.listdir(UPLOAD_DIR))
            new_files = after_files - initial_files
            self.assertEqual(len(new_files), 0, f"Orphan files left on disk: {new_files}")

        asyncio.run(run_test())

    def test_background_parsing_uses_worker_thread(self):
        """Verify _process_uploaded_document offloads parsing via asyncio.to_thread."""
        import inspect
        from app.routes import pdf_routes
        source = inspect.getsource(pdf_routes._process_uploaded_document)

        self.assertIn("asyncio.to_thread", source, "CPU-bound parsing must be offloaded via asyncio.to_thread")


if __name__ == "__main__":
    unittest.main()
