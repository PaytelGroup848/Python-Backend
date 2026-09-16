"""
BUG-06: Regression Test for Developer Portal Python Code Snippet Validity
"""
import os
import unittest


class TestBug06PythonSnippet(unittest.TestCase):

    def setUp(self):
        self.modal_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "ai-platform-frontend",
                "src", "features", "chat", "components", "api-keys-modal.tsx"
            )
        )

    def test_python_snippet_syntax_validity(self):
        """Verify Python code snippet in api-keys-modal.tsx is syntactically valid when compiled."""
        self.assertTrue(os.path.exists(self.modal_path), f"File not found: {self.modal_path}")

        with open(self.modal_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Assert no double double-quotes on base_url
        self.assertNotIn('base_url=""https://', content, "Double double-quote syntax error must be eliminated")
        self.assertIn('base_url="https://api.patwatoliai.com/v1"', content)

        # Extract snippet and compile with Python
        start_marker = "const pythonCode = `"
        end_marker = "`;"
        self.assertIn(start_marker, content)

        idx1 = content.find(start_marker) + len(start_marker)
        idx2 = content.find(end_marker, idx1)
        raw_snippet = content[idx1:idx2]

        # Replace JS template literal variables with dummy strings
        import re
        py_snippet = re.sub(r"\$\{[^}]+\}", "dummy_api_key", raw_snippet)

        # Assert it compiles cleanly
        try:
            compiled = compile(py_snippet, "<generated_snippet>", "exec")
            self.assertIsNotNone(compiled)
        except SyntaxError as e:
            self.fail(f"Generated Python snippet failed syntax compilation: {e}")


if __name__ == "__main__":
    unittest.main()

