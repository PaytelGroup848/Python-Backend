"""
BUG-09: Regression Test for Developer API Key Service Token Refresh & ApiClient Integration
Verifies that api-key-service.ts uses the centralized apiClient (which handles 401 token refresh)
rather than raw unintercepted fetch().
"""
import os
import unittest


class TestBug09ApiKeyRefresh(unittest.TestCase):

    def setUp(self):
        self.service_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "ai-platform-frontend",
                "src", "features", "chat", "services", "api-key-service.ts"
            )
        )

    def test_api_key_service_uses_central_api_client(self):
        """Verify api-key-service.ts imports apiClient and eliminates raw unintercepted fetch calls."""
        self.assertTrue(os.path.exists(self.service_path), f"File not found: {self.service_path}")
        with open(self.service_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Must import apiClient
        self.assertIn('import { apiClient } from "@/services/api/client"', content)

        # Must use apiClient methods
        self.assertIn("apiClient.get", content)
        self.assertIn("apiClient.post", content)
        self.assertIn("apiClient.delete", content)

        # Must not contain raw unintercepted window.fetch or fetch() calls for api keys
        self.assertNotIn("fetch(", content)
        self.assertNotIn("window.fetch(", content)


if __name__ == "__main__":
    unittest.main()

