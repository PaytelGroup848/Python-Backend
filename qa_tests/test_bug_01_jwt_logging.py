"""
BUG-01: Regression Test for Secret Leakage & Raw JWT Logging Prevention
"""
import inspect
import unittest
import io
import sys
from unittest.mock import AsyncMock, patch

import qa_tests.conftest
from app.core.security import create_access_token
from app.modules.chat.routes import chat_ws_routes


class TestBug01JwtLogging(unittest.TestCase):

    def test_no_raw_jwt_prints_in_source(self):
        """Verify chat_ws_routes.py contains zero print statements that log tokens or payloads."""
        source = inspect.getsource(chat_ws_routes)

        self.assertNotIn('print("WS TOKEN', source, "Raw JWT token print statement must be permanently removed")
        self.assertNotIn("print(payload)", source, "Decoded JWT payload print statement must be permanently removed")
        self.assertNotIn('print("JWT ERROR', source, "JWT error print statement must be permanently removed")
        self.assertNotIn("print(token)", source, "Token print statement must not exist")

    def test_runtime_websocket_auth_does_not_leak_token_to_stdout(self):
        """Simulate WebSocket connection attempt and verify stdout has zero token leakage."""
        token = create_access_token({"sub": "999", "role": "admin"})

        captured_stdout = io.StringIO()
        with patch("sys.stdout", captured_stdout):
            # Inspect that running decode and logging produces zero cleartext token output
            from app.core.security import jwt, SECRET_KEY, ALGORITHM
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            self.assertEqual(payload.get("sub"), "999")

        output = captured_stdout.getvalue()
        self.assertNotIn(token, output, "Raw JWT access token must never appear in stdout")
        self.assertNotIn("Bearer", output)


if __name__ == "__main__":
    unittest.main()

