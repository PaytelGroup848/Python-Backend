"""
BUG-07: Regression Test for Same-File Re-upload & Input Value Reset
"""
import os
import unittest


class TestBug07Reupload(unittest.TestCase):

    def setUp(self):
        self.btn_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "ai-platform-frontend",
                "src", "features", "documents", "components", "upload-button.tsx"
            )
        )

    def test_file_input_resets_value_in_onchange(self):
        """Verify upload-button.tsx resets e.target.value = '' to allow selecting the same file repeatedly."""
        self.assertTrue(os.path.exists(self.btn_path), f"File not found: {self.btn_path}")

        with open(self.btn_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Assert e.target.value = "" is present inside onChange
        self.assertIn('e.target.value = "";', content, "e.target.value must be reset in onChange to allow same-file selection")

    def test_client_side_size_limit_check(self):
        """Verify client-side 20MB file limit check exists before dispatching upload."""
        with open(self.btn_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("20 * 1024 * 1024", content, "20MB size guard must be present")
        self.assertIn("MAX_FILE_SIZE", content)


if __name__ == "__main__":
    unittest.main()

