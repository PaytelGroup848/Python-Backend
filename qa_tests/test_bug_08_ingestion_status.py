"""
BUG-08: Regression Test for Document Ingestion Status Polling & Authoritative Tracking
"""
import os
import unittest


class TestBug08IngestionStatus(unittest.TestCase):

    def setUp(self):
        self.doc_service_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "ai-platform-frontend",
                "src", "features", "documents", "services", "document-service.ts"
            )
        )
        self.upload_btn_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "ai-platform-frontend",
                "src", "features", "documents", "components", "upload-button.tsx"
            )
        )

    def test_document_service_implements_get_job_status(self):
        """Verify document-service.ts exports getJobStatus targeting /pdf/job-status/{job_id}."""
        self.assertTrue(os.path.exists(self.doc_service_path))
        with open(self.doc_service_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("export async function getJobStatus", content)
        self.assertIn("/pdf/job-status/", content)
        self.assertIn("DocumentJobStatus", content)

    def test_upload_button_polls_status_and_handles_terminal_states(self):
        """Verify upload-button.tsx implements pollStatus, tracks 'completed' and 'failed', and cleans up on unmount."""
        self.assertTrue(os.path.exists(self.upload_btn_path))
        with open(self.upload_btn_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("pollStatus", content)
        self.assertIn('"completed"', content)
        self.assertIn('"failed"', content)
        self.assertIn("clearInterval(pollTimerRef.current)", content, "Must clean up interval timer to prevent memory leaks")


if __name__ == "__main__":
    unittest.main()

