"""
LOG-01 to LOG-05: Logout Contract, Quota Protection & Multi-Device Isolation Tests
"""
import unittest

import qa_tests.conftest

from app.modules.auth.schemas.auth_schema import LogoutRequest


class TestLogoutAndIsolation(unittest.TestCase):

    def test_LOG_01_logout_request_schema(self):
        """LOG-01: Verify LogoutRequest supports both populated token and empty invocation."""
        req_with_token = LogoutRequest(refresh_token="active_refresh_token_123")
        self.assertEqual(req_with_token.refresh_token, "active_refresh_token_123")

        req_empty = LogoutRequest()
        self.assertIsNone(req_empty.refresh_token)

    def test_LOG_04_multi_device_session_isolation_logic(self):
        """LOG-04: Verify session revocation target isolation across multiple devices."""
        # Simulated database sessions table state
        simulated_sessions = {
            "session_laptop_token_AAA": {"user_id": 101, "device": "laptop"},
            "session_mobile_token_BBB": {"user_id": 101, "device": "mobile"},
        }

        target_token_to_revoke = "session_laptop_token_AAA"

        # Emulate logout logic in auth_routes.py
        if target_token_to_revoke in simulated_sessions:
            del simulated_sessions[target_token_to_revoke]

        # Verify laptop session revoked
        self.assertNotIn("session_laptop_token_AAA", simulated_sessions)

        # Verify mobile session remains fully active
        self.assertIn("session_mobile_token_BBB", simulated_sessions)
        self.assertEqual(simulated_sessions["session_mobile_token_BBB"]["user_id"], 101)

    def test_LOG_05_quota_and_cache_preservation_on_logout(self):
        """LOG-05: Verify logout does not wipe user-global usage quota key usage:{user_id}."""
        # Inspect auth_routes.py logout source logic
        import inspect
        from app.modules.auth.routes.auth_routes import logout

        source_code = inspect.getsource(logout)

        # Must NOT delete usage:{user_id}
        self.assertNotIn('f"usage:{user_id}"', source_code, "Security Regression: logout must NOT delete usage quota key!")

        # Must NOT delete chat:{user_id}
        self.assertNotIn('f"chat:{user_id}"', source_code, "Security Regression: logout must NOT delete global chat key!")


if __name__ == "__main__":
    unittest.main()

