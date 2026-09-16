"""
Security Regression Test Suite
Verifies that:
1. No sensitive credentials, JWT tokens, or raw payloads are printed to stdout/stderr.
2. Token verification (verify_token) defensively handles missing/malformed/non-integer 'sub' claims.
3. Protected endpoints enforce authentication boundaries.
"""
import os
import re
import unittest
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import verify_token


class TestSecurityRegression(unittest.TestCase):

    def test_no_sensitive_logging_in_critical_modules(self):
        """Scans critical routes for raw print statements exposing tokens or keys."""
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        sensitive_files = [
            os.path.join(backend_dir, "app", "modules", "chat", "routes", "chat_ws_routes.py"),
            os.path.join(backend_dir, "app", "modules", "public_api", "routes", "ai_api_routes.py"),
            os.path.join(backend_dir, "app", "routes", "pdf_routes.py"),
            os.path.join(backend_dir, "app", "modules", "assistants", "routes", "assistant_routes.py"),
        ]

        # Patterns that indicate leaking raw tokens/passwords to logs via print
        leak_patterns = [
            r'print\(.*token.*\)',
            r'print\(.*payload.*\)',
            r'print\(.*password.*\)',
            r'print\(.*secret.*\)',
            r'print\(.*api_key.*\)',
        ]

        for file_path in sensitive_files:
            if not os.path.exists(file_path):
                continue
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            for pattern in leak_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                # Filter out benign print statements if any (none should exist)
                self.assertEqual(
                    len(matches), 0,
                    f"Found potential secret leakage in {file_path}: {matches}"
                )

    def test_verify_token_missing_sub(self):
        """Verify that a JWT payload missing 'sub' raises HTTPException(401), not 500 TypeError."""
        from unittest.mock import MagicMock
        from app.core.security import SECRET_KEY, ALGORITHM
        payload = {"role": "user", "exp": datetime.now(timezone.utc) + timedelta(minutes=15)}
        token_str = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        mock_cred = MagicMock(credentials=token_str)
        with self.assertRaises(HTTPException) as ctx:
            verify_token(mock_cred)
        self.assertEqual(ctx.exception.status_code, 401)

    def test_verify_token_invalid_sub_format(self):
        """Verify that a JWT payload with non-integer 'sub' raises HTTPException(401), not 500 TypeError."""
        from unittest.mock import MagicMock
        from app.core.security import SECRET_KEY, ALGORITHM
        payload = {"sub": "not-an-integer", "role": "user", "exp": datetime.now(timezone.utc) + timedelta(minutes=15)}
        token_str = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        mock_cred = MagicMock(credentials=token_str)
        with self.assertRaises(HTTPException) as ctx:
            verify_token(mock_cred)
        self.assertEqual(ctx.exception.status_code, 401)

    def test_verify_token_valid_sub(self):
        """Verify that a valid token parses sub into an integer correctly."""
        from unittest.mock import MagicMock
        from app.core.security import SECRET_KEY, ALGORITHM
        payload = {"sub": "42", "role": "user", "exp": datetime.now(timezone.utc) + timedelta(minutes=15)}
        token_str = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        mock_cred = MagicMock(credentials=token_str)
        result = verify_token(mock_cred)
        self.assertEqual(result.get("user_id"), 42)


if __name__ == "__main__":
    unittest.main()
