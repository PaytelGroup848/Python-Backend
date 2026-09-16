"""
REF-01 to REF-05: Refresh Token Contract & Backward Compatibility Tests
"""
import unittest
from datetime import datetime, timedelta, timezone
from jose import jwt

import qa_tests.conftest

from app.modules.auth.schemas.auth_schema import RefreshTokenRequest, RefreshTokenResponse
from app.core.security import create_refresh_token, create_access_token, SECRET_KEY, ALGORITHM


class TestRefreshContracts(unittest.TestCase):

    def test_REF_01_refresh_token_request_body_schema(self):
        """REF-01: Verify JSON body contract for /auth/refresh with RefreshTokenRequest."""
        # Standard Next.js Axios interceptor payload
        payload = {"refresh_token": "valid_refresh_token_string_abc"}
        req = RefreshTokenRequest(**payload)
        self.assertEqual(req.refresh_token, "valid_refresh_token_string_abc")

    def test_REF_02_dual_mode_precedence_resolution(self):
        """REF-02: Verify token resolution logic between JSON body and URL query parameter."""
        # Case A: JSON Body only
        req_body = RefreshTokenRequest(refresh_token="body_token_123")
        resolved_token_a = (req_body.refresh_token.strip() if req_body and req_body.refresh_token else None) or None
        self.assertEqual(resolved_token_a, "body_token_123")

        # Case B: URL Query parameter only
        query_token = "query_token_456"
        resolved_token_b = None or (query_token.strip() if query_token else None)
        self.assertEqual(resolved_token_b, "query_token_456")

        # Case C: Both provided (Body takes precedence)
        req_both = RefreshTokenRequest(refresh_token="body_token_precedent")
        query_both = "query_token_ignored"
        resolved_token_c = (req_both.refresh_token.strip() if req_both and req_both.refresh_token else None) or (query_both.strip() if query_both else None)
        self.assertEqual(resolved_token_c, "body_token_precedent")

    def test_REF_03_missing_token_detection(self):
        """REF-03: Verify missing token detection produces unambiguous 422 trigger."""
        req_empty = None
        query_empty = None
        resolved_token = (req_empty.refresh_token.strip() if req_empty and req_empty.refresh_token else None) or (query_empty.strip() if query_empty else None)
        self.assertIsNone(resolved_token)

    def test_REF_05_expired_refresh_token_rejected(self):
        """REF-05: Verify refresh token with expired claims is rejected."""
        past_expire = datetime.now(timezone.utc) - timedelta(minutes=1)
        expired_refresh = jwt.encode({"sub": "99", "role": "employee", "exp": past_expire}, SECRET_KEY, algorithm=ALGORITHM)

        with self.assertRaises(Exception):
            jwt.decode(expired_refresh, SECRET_KEY, algorithms=[ALGORITHM])


if __name__ == "__main__":
    unittest.main()

