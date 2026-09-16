"""
FE-01 to FE-03: Frontend Auth Contract, Interceptor & Logout Verification Tests
"""
import os
import unittest


class TestFrontendContracts(unittest.TestCase):

    def setUp(self):
        self.frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ai-platform-frontend"))

    def test_FE_01_interceptor_sends_json_body_refresh(self):
        """FE-01: Verify Axios response interceptor sends refresh_token in JSON request body."""
        client_ts_path = os.path.join(self.frontend_dir, "src", "services", "api", "client.ts")
        self.assertTrue(os.path.exists(client_ts_path), f"File missing: {client_ts_path}")

        with open(client_ts_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Interceptor must catch 401 and post to /auth/refresh with JSON object
        self.assertIn('error.response?.status === 401', content)
        self.assertIn('/auth/refresh', content)
        self.assertIn('refresh_token:', content)

    def test_FE_02_sequential_logout_with_guaranteed_cleanup(self):
        """FE-02 & FE-03: Verify auth-store logout sequentially revokes backend and cleans storage in finally."""
        store_ts_path = os.path.join(self.frontend_dir, "src", "stores", "auth-store.ts")
        self.assertTrue(os.path.exists(store_ts_path), f"File missing: {store_ts_path}")

        with open(store_ts_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Verify sequential logout structure
        self.assertIn('logout: async () =>', content)
        self.assertIn('/auth/logout', content)
        self.assertIn('refresh_token: refreshToken', content)
        self.assertIn('finally {', content)
        self.assertIn('user: null', content)
        self.assertIn('accessToken: null', content)
        self.assertIn('refreshToken: null', content)

        # Verify safe console logging (no token or raw error object logged)
        self.assertIn('console.warn("Backend session revocation failed; proceeding with local logout.");', content)
        self.assertNotIn('console.warn(err', content)
        self.assertNotIn('console.log(refreshToken', content)


if __name__ == "__main__":
    unittest.main()

