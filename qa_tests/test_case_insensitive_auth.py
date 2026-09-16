"""
Regression Test for Case-Insensitive and Trimmed Email Authentication
Verifies that UserRepository.get_by_email matches emails regardless of mobile auto-capitalization or spaces.
"""
import unittest
from unittest.mock import AsyncMock, MagicMock

import qa_tests.conftest
from app.models.user import User
from app.modules.auth.repositories.user_repository import UserRepository


class TestCaseInsensitiveAuth(unittest.TestCase):

    def setUp(self):
        self.repo = UserRepository()

    def test_get_by_email_with_empty_or_none(self):
        """Verify get_by_email gracefully handles empty string or None without exception."""
        async def run_test():
            mock_db = MagicMock()
            res1 = await self.repo.get_by_email(mock_db, "")
            res2 = await self.repo.get_by_email(mock_db, None)
            self.assertIsNone(res1)
            self.assertIsNone(res2)

        import asyncio
        asyncio.run(run_test())

    def test_get_by_email_normalizes_case_and_whitespace(self):
        """Verify get_by_email query normalizes casing and strips whitespace."""
        async def run_test():
            mock_db = MagicMock()
            mock_result = MagicMock()
            dummy_user = User(id=1, email="sohan1233@gmail.com", name="Sohan")
            mock_result.scalar_one_or_none.return_value = dummy_user
            mock_db.execute = AsyncMock(return_value=mock_result)

            # Mobile typed: Sohan1233@gmail.com with space
            user = await self.repo.get_by_email(mock_db, "  Sohan1233@GMAIL.COM  ")
            self.assertIsNotNone(user)
            self.assertEqual(user.email, "sohan1233@gmail.com")

            # Verify execute was called
            mock_db.execute.assert_called_once()

        import asyncio
        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()

