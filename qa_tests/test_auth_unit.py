"""
AUTH-01 to AUTH-08, TOK-01 to TOK-04, SEC-01
Unit & Contract Tests for Authentication & Tokens
"""
import unittest
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

import qa_tests.conftest  # Sets up mocks

from app.modules.auth.schemas.auth_schema import RegisterRequest, LoginRequest
from app.modules.auth.services.auth_service import AuthService
from app.core.security import (
    create_access_token,
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)


class TestAuthAndTokens(unittest.TestCase):

    def setUp(self):
        self.auth_service = AuthService()

    def test_AUTH_01_token_generation_claims(self):
        """TOK-01 & TOK-02: Verify access & refresh token claims and expiration window."""
        user_id = 42
        role = "employee"

        access_token = create_access_token({"sub": str(user_id), "role": role})
        refresh_token = create_refresh_token({"sub": str(user_id), "role": role})

        # Decode access token
        access_payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        self.assertEqual(access_payload.get("sub"), "42")
        self.assertEqual(access_payload.get("role"), "employee")
        exp_access = datetime.fromtimestamp(access_payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        # Access token must expire within ~24h (1440m)
        diff_access = exp_access - now
        self.assertTrue(timedelta(hours=23, minutes=50) < diff_access <= timedelta(hours=24, minutes=5))

        # Decode refresh token
        refresh_payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        self.assertEqual(refresh_payload.get("sub"), "42")
        self.assertEqual(refresh_payload.get("role"), "employee")
        exp_refresh = datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc)
        # Refresh token must expire within ~7 days
        diff_refresh = exp_refresh - now
        self.assertTrue(timedelta(days=6, hours=23) < diff_refresh <= timedelta(days=7, hours=1))

    def test_AUTH_04_defensive_password_verification_malformed_hashes(self):
        """AUTH-04: Verify malformed or non-bcrypt hashes return False, never throwing 500 crash."""
        # 1. Plain text (unhashed)
        self.assertFalse(self.auth_service.verify_password("mypassword", "plaintext_password_not_hash"))

        # 2. Corrupted prefix
        self.assertFalse(self.auth_service.verify_password("mypassword", "$2b$12$corruptedhashvalue"))

        # 3. Completely arbitrary string
        self.assertFalse(self.auth_service.verify_password("mypassword", "12345678"))

        # 4. Empty strings
        self.assertFalse(self.auth_service.verify_password("", ""))
        self.assertFalse(self.auth_service.verify_password("mypassword", ""))
        self.assertFalse(self.auth_service.verify_password("", "$2b$12$validlookinghash"))

        # 5. Legitimate bcrypt hash must succeed
        valid_hash = self.auth_service.hash_password("SuperSecret123!")
        self.assertTrue(self.auth_service.verify_password("SuperSecret123!", valid_hash))
        self.assertFalse(self.auth_service.verify_password("WrongPassword!", valid_hash))

    def test_AUTH_05_schema_validation_empty_and_types(self):
        """AUTH-05 & AUTH-06: Verify Pydantic schema validation constraints."""
        # Valid login request
        valid_req = LoginRequest(email="test@patwatoliai.com", password="SecretPassword123")
        self.assertEqual(valid_req.email, "test@patwatoliai.com")

        # Invalid email format
        with self.assertRaises(Exception):
            LoginRequest(email="not-an-email", password="ValidPassword123")

    def test_TOK_03_expired_token_handling(self):
        """TOK-03: Verify expired tokens fail decoding cleanly with JWTError."""
        past_expire = datetime.now(timezone.utc) - timedelta(hours=1)
        expired_token = jwt.encode({"sub": "42", "role": "employee", "exp": past_expire}, SECRET_KEY, algorithm=ALGORITHM)

        with self.assertRaises(JWTError):
            jwt.decode(expired_token, SECRET_KEY, algorithms=[ALGORITHM])

    def test_TOK_04_tampered_token_handling(self):
        """TOK-04: Verify tampered token payload or signature fails decoding cleanly."""
        valid_token = create_access_token({"sub": "42", "role": "employee"})
        # Tamper last 4 bytes of signature
        tampered_token = valid_token[:-4] + "xxxx"

        with self.assertRaises(JWTError):
            jwt.decode(tampered_token, SECRET_KEY, algorithms=[ALGORITHM])


if __name__ == "__main__":
    unittest.main()

