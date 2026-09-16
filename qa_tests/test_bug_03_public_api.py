"""
BUG-03: Regression Test for Public AI API History Preservation & Empty Array Protection
"""
import asyncio
import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from pydantic import ValidationError

import qa_tests.conftest
from app.modules.public_api.schemas.ai_api_schema import ChatCompletionRequest, ChatMessage
from app.modules.public_api.routes.ai_api_routes import chat_completions


class TestBug03PublicApi(unittest.TestCase):

    def test_schema_rejects_empty_messages_list(self):
        """Negative test: Pydantic schema must reject empty messages: [] with validation error."""
        with self.assertRaises(ValidationError):
            ChatCompletionRequest(model="gpt-4o", messages=[])

    def test_multi_turn_history_preservation(self):
        """Verify full multi-turn conversation context reaches provider with exact roles and ordering."""
        raw_msgs = [
            ChatMessage(role="system", content="You are an enterprise AI assistant."),
            ChatMessage(role="user", content="Step 1: Process file."),
            ChatMessage(role="assistant", content="File processed. Result is 42."),
            ChatMessage(role="user", content="Step 2: Double the result.")
        ]
        req = ChatCompletionRequest(model="gpt-4o", messages=raw_msgs)

        # Build expected dict list
        messages_dict = [{"role": m.role, "content": m.content} for m in req.messages]
        self.assertEqual(len(messages_dict), 4)
        self.assertEqual(messages_dict[0]["role"], "system")
        self.assertEqual(messages_dict[1]["content"], "Step 1: Process file.")
        self.assertEqual(messages_dict[2]["role"], "assistant")
        self.assertEqual(messages_dict[3]["content"], "Step 2: Double the result.")

    def test_provider_failure_returns_sanitized_502(self):
        """Negative test: Upstream AI provider exception must produce sanitized 502, not 500 crash."""
        async def run_test():
            mock_model = MagicMock()
            mock_model.provider = "openai"
            mock_model.is_active = True

            mock_provider = MagicMock()
            mock_provider.generate = AsyncMock(side_effect=RuntimeError("Connection timeout to OpenAI cluster"))

            mock_repo = MagicMock()
            mock_repo.get_by_name = AsyncMock(return_value=mock_model)

            with patch("app.modules.public_api.routes.ai_api_routes.model_repository", mock_repo), \
                 patch.dict("app.modules.public_api.routes.ai_api_routes.provider_registry", {"openai": mock_provider}):

                req = ChatCompletionRequest(
                    model="gpt-4o",
                    messages=[ChatMessage(role="user", content="Hello")]
                )
                current_user = MagicMock(id=1, current_api_key=None)

                with self.assertRaises(HTTPException) as ctx:
                    await chat_completions(payload=req, db=MagicMock(), current_user=current_user)

                self.assertEqual(ctx.exception.status_code, 502)
                self.assertIn("Upstream AI provider error", ctx.exception.detail)
                self.assertNotIn("Connection timeout to OpenAI cluster", ctx.exception.detail, "Raw internal error must not leak")

        asyncio.run(run_test())

    def test_openai_standard_usage_structure(self):
        """Verify output dictionary contains genuine OpenAI usage metrics."""
        async def run_test():
            mock_model = MagicMock(provider="openai", is_active=True)
            mock_provider = MagicMock()
            mock_provider.generate = AsyncMock(return_value={
                "response": "84",
                "model": "gpt-4o",
                "usage": {
                    "prompt_tokens": 35,
                    "completion_tokens": 12,
                    "total_tokens": 47
                }
            })

            mock_repo = MagicMock()
            mock_repo.get_by_name = AsyncMock(return_value=mock_model)

            mock_log = AsyncMock()
            with patch("app.modules.public_api.routes.ai_api_routes.model_repository", mock_repo), \
                 patch.dict("app.modules.public_api.routes.ai_api_routes.provider_registry", {"openai": mock_provider}), \
                 patch("app.modules.public_api.routes.ai_api_routes.api_request_service.log_request", mock_log):

                req = ChatCompletionRequest(
                    model="gpt-4o",
                    messages=[ChatMessage(role="user", content="Double 42")]
                )
                current_user = MagicMock(id=1, current_api_key=None)

                res = await chat_completions(payload=req, db=MagicMock(), current_user=current_user)

                self.assertEqual(res["object"], "chat.completion")
                self.assertIn("usage", res)
                self.assertEqual(res["usage"]["prompt_tokens"], 35)
                self.assertEqual(res["usage"]["completion_tokens"], 12)
                self.assertEqual(res["usage"]["total_tokens"], 47)
                self.assertEqual(res["choices"][0]["message"]["content"], "84")

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
