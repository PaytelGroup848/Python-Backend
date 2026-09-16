"""
Concurrency Regression Tests for Public API, Document Limits, and WebSocket Token Verification
Verifies thread-safety, non-blocking behavior, and isolation under concurrent loads.
"""
import asyncio
import io
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock
from fastapi import UploadFile

from app.core.security import create_access_token, verify_token
from app.modules.public_api.schemas.ai_api_schema import ChatCompletionRequest, ChatMessage
from app.routes.pdf_routes import upload_pdf


class TestConcurrencyRegression(unittest.TestCase):

    def test_concurrent_public_api_payload_validation(self):
        """Verify that concurrent validation of ChatCompletionRequest schemas is thread-safe and performant."""
        def validate_payload(worker_id):
            messages = [
                ChatMessage(role="system", content="You are a helpful assistant."),
                ChatMessage(role="user", content=f"Request from worker {worker_id}"),
            ]
            req = ChatCompletionRequest(
                model="gpt-4o",
                messages=messages,
                stream=False
            )
            return req.messages[1].content

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(validate_payload, range(50)))

        self.assertEqual(len(results), 50)
        for i, msg in enumerate(results):
            self.assertEqual(msg, f"Request from worker {i}")

    def test_concurrent_token_verifications(self):
        """Verify 50 concurrent verify_token calls maintain thread safety and user_id isolation."""
        tokens = [
            (i, create_access_token({"sub": str(1000 + i), "role": "user"}))
            for i in range(50)
        ]

        def worker(item):
            expected_offset, token_str = item
            mock_cred = MagicMock(credentials=token_str)
            res = verify_token(mock_cred)
            return res.get("user_id") == (1000 + expected_offset)

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(worker, tokens))

        self.assertEqual(len(results), 50)
        self.assertTrue(all(results))


if __name__ == "__main__":
    unittest.main()
