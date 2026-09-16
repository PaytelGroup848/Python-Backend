"""
Production Regression Suite: General Chat Accuracy, Context Isolation & Pipeline Hardening
Covers BUG-01 to BUG-10 mandates from CTO.
"""
import asyncio
import json
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import qa_tests.conftest

from app.services.agent_service import (
    ContextBuilderService,
    IntentClassifierService,
    IntentType,
    router,
    retrieval_node,
    preprocessing_node,
    generation_node,
    run_agent,
    AgentRuntime,
    MAX_MEMORY_MESSAGES
)
from app.modules.providers.groq_provider import GroqProvider, MODEL_NAME as GROQ_MODEL_NAME
from app.modules.providers.gemini_provider import GeminiProvider, MODEL_NAME as GEMINI_MODEL_NAME
from app.modules.providers.provider_health import provider_health_service
from app.modules.provider_runtime.manager.provider_runtime_manager import provider_runtime_manager


class TestGeneralChatAccuracy(unittest.IsolatedAsyncioTestCase):

    # =========================================================================
    # BUG-01: DOCUMENT CONTEXT POISONING & CONTEXT ISOLATION
    # =========================================================================

    async def test_BUG_01_general_chat_does_not_inherit_historical_pdf(self):
        """
        Verify that a General Chat request with no attached documents does NOT
        inherit old document state from redis key latest_pdf:{user_id}.
        """
        user_id = 999
        session_id = "clean_conv_session_123"

        # Mock Redis client so latest_pdf exists from an earlier upload,
        # but the active session has NO conversation_pdf.
        mock_redis = AsyncMock()
        async def fake_redis_get(key):
            if key == f"latest_pdf:{user_id}":
                return "old_unrelated_invoice_2024.pdf"
            if key == f"conversation_pdf:{session_id}":
                return None
            return None
        mock_redis.get.side_effect = fake_redis_get

        state = {
            "query": "What is photosynthesis?",
            "rewritten_query": "",
            "session_id": session_id,
            "user_id": user_id,
            "assistant_id": None,
            "user_role": "employee",
            "user_department": "general",
            "rag_enabled": False,
            "context": "",
            "sources": [],
            "attached_docs": [],
            "web_search": False,
        }

        with patch("app.shared.redis.client.redis_client", mock_redis):
            res = await retrieval_node(state)

        # Assert no old invoice context or sources entered the state
        self.assertEqual(res.get("context", ""), "", "Context must remain empty for unattached general chat")
        self.assertEqual(res.get("sources", []), [], "Sources must not cite old historical documents")

    async def test_BUG_01_explicit_document_attachment_is_preserved(self):
        """
        Verify that when a document IS explicitly attached to the current request,
        it is correctly loaded and parsed.
        """
        session_id = "doc_conv_session_456"
        user_id = 888

        state = {
            "query": "Summarize the attached document.",
            "rewritten_query": "",
            "session_id": session_id,
            "user_id": user_id,
            "assistant_id": None,
            "user_role": "employee",
            "user_department": "general",
            "rag_enabled": False,
            "context": "",
            "sources": [],
            "attached_docs": ["annual_report_2025.pdf"],
            "web_search": False,
        }

        mock_db = AsyncMock()
        mock_scalar = MagicMock()
        mock_doc = MagicMock()
        mock_doc.file_path = "/tmp/annual_report_2025.pdf"
        mock_scalar.scalar_one_or_none.return_value = mock_doc
        mock_db.execute.return_value = mock_scalar

        mock_session_ctx = MagicMock()
        mock_session_ctx.__aenter__.return_value = mock_db
        mock_session_ctx.__aexit__.return_value = None

        fake_pages = [{"text": "Total revenue for 2025 was $50M.", "page_number": 1}]

        with patch("app.services.agent_service.AsyncSessionLocal", return_value=mock_session_ctx), \
             patch("app.services.document_parser_service.parse_document", AsyncMock(return_value=fake_pages)):
            res = await retrieval_node(state)

        self.assertIn("USER ATTACHED DOCUMENT (annual_report_2025.pdf)", res.get("context", ""))
        self.assertIn("Total revenue for 2025 was $50M.", res.get("context", ""))
        self.assertTrue(any(s.get("source_file") == "annual_report_2025.pdf" for s in res.get("sources", [])))

    # =========================================================================
    # BUG-02: TOKEN-BUDGET-AWARE PROMPT & QUESTION PRESERVATION
    # =========================================================================

    def test_BUG_02_user_question_is_never_truncated_in_long_prompt(self):
        """
        Construct a request with long system prompt, long memory, and long context.
        Verify that the complete current user question is preserved 100% intact.
        """
        very_long_system = "System Rule: " + ("You are a strict Patwatoli AI assistant. " * 50)
        very_long_memory = "\n".join([f"User: Message {i}\nAssistant: Long detailed response {i}" for i in range(20)])
        very_long_context = "=== DOCUMENT DATA ===\n" + ("Fact and statistics chunk line. " * 1500)
        user_question = "CRITICAL_QUESTION: How do I implement a non-blocking WebSocket in asyncio?"

        prompt = ContextBuilderService.build_prompt(
            query=user_question,
            system_prompt=very_long_system,
            memory=very_long_memory,
            context=very_long_context,
            plan="1. Step one plan\n2. Step two plan",
            max_total_chars=10000
        )

        # The user's question must appear completely intact in the final prompt
        self.assertIn(user_question, prompt, "User question must never be truncated")
        self.assertIn("CORE PLATFORM DIRECTIVE", prompt, "System brand directive must be preserved")
        self.assertIn("CENTRAL LANGUAGE & SCRIPT DIRECTIVE", prompt, "Language directive must be preserved")

    def test_BUG_02_groq_provider_does_not_truncate_prompts_under_100k(self):
        """
        Verify that GroqProvider does NOT truncate prompts that are within reasonable context.
        """
        provider = GroqProvider()
        test_text = "A" * 8000  # 8000 chars was previously destroyed by 4000/2000 char truncation
        msg = [{"role": "user", "content": test_text}]

        # Using a mock for http_client
        mock_post = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}],
            "usage": {"total_tokens": 100}
        }
        mock_post.return_value = mock_resp

        with patch("app.modules.providers.groq_provider.http_client.post", mock_post):
            asyncio.run(provider.generate(messages=msg))

        sent_payload = mock_post.call_args[1]["json"]
        sent_content = sent_payload["messages"][0]["content"]
        self.assertEqual(len(sent_content), 8000, "Prompt must not be truncated at 2000 or 4000 chars")

    # =========================================================================
    # BUG-03: MODEL NAME VALIDITY & FALLBACK UNBOUNDLOCALERROR
    # =========================================================================

    def test_BUG_03_groq_model_name_syntax_validity(self):
        """
        Verify GroqProvider.MODEL_NAME is a clean valid string and not a corrupted concatenation.
        """
        self.assertNotIn("qwen3.8", GROQ_MODEL_NAME, "Model name must not concatenate two model names")
        self.assertTrue(GROQ_MODEL_NAME.startswith("llama-") or GROQ_MODEL_NAME.startswith("qwen-"),
                        f"Expected valid model, got: {GROQ_MODEL_NAME}")

    async def test_BUG_03_provider_fallback_does_not_crash_with_unbound_latency(self):
        """
        Simulate primary provider stream throwing an exception.
        Verify fallback executes and does NOT crash with UnboundLocalError: latency.
        """
        primary_mock = MagicMock()
        async def failing_stream(*args, **kwargs):
            raise ConnectionError("Primary upstream connection lost")
            yield  # Make it an async generator
        primary_mock.stream_chat = failing_stream

        fallback_mock = MagicMock()
        async def working_stream(*args, **kwargs):
            yield "Fallback token 1 "
            yield "Fallback token 2"
        fallback_mock.stream_chat = working_stream

        mock_health = AsyncMock()
        mock_health.get_best_provider.side_effect = ["primary", "fallback"]

        with patch.dict(provider_runtime_manager.providers, {"primary": primary_mock, "fallback": fallback_mock}, clear=True), \
             patch("app.modules.provider_runtime.manager.provider_runtime_manager.provider_health_service", mock_health):

            collected = []
            async for chunk in provider_runtime_manager.stream_response("Hello"):
                collected.append(chunk)

            self.assertEqual("".join(collected), "Fallback token 1 Fallback token 2")

    async def test_BUG_03_both_providers_fail_returns_sanitized_error(self):
        """
        Simulate both primary and fallback failing.
        Verify it raises a clean RuntimeError rather than exposing internal keys or tracebacks.
        """
        primary_mock = MagicMock()
        async def failing_stream_1(*args, **kwargs):
            raise TimeoutError("Cluster timeout")
            yield
        primary_mock.stream_chat = failing_stream_1

        fallback_mock = MagicMock()
        async def failing_stream_2(*args, **kwargs):
            raise RuntimeError("API quota exhausted")
            yield
        fallback_mock.stream_chat = failing_stream_2

        mock_health = AsyncMock()
        mock_health.get_best_provider.side_effect = ["primary", "fallback"]

        with patch.dict(provider_runtime_manager.providers, {"primary": primary_mock, "fallback": fallback_mock}, clear=True), \
             patch("app.modules.provider_runtime.manager.provider_runtime_manager.provider_health_service", mock_health):

            with self.assertRaises(RuntimeError) as ctx:
                async for _ in provider_runtime_manager.stream_response("Hello"):
                    pass
            self.assertIn("unavailable", str(ctx.exception).lower())

    # =========================================================================
    # BUG-04: RAW CONTEXT MUST NEVER BECOME THE ANSWER
    # =========================================================================

    async def test_BUG_04_raw_context_never_exposed_on_failure(self):
        """
        Security Regression: Context contains INTERNAL_TEST_MARKER_12345.
        Force streaming and batch generation to fail.
        Verify final response does NOT contain INTERNAL_TEST_MARKER_12345 or raw context prefix.
        """
        secret_marker = "INTERNAL_TEST_MARKER_12345"
        state = {
            "query": "Give me system secrets",
            "context": f"Confidential internal notes: {secret_marker}",
            "system_prompt": "Assistant",
            "memory_context": "",
            "tool_result": {},
            "plan": "",
            "user_id": 101,
            "temperature": 0.2,
            "stream_handler": AsyncMock(),
            "web_sources": [],
            "language": "en"
        }

        # Mock usage service to allow
        mock_usage = AsyncMock()
        mock_usage.check_usage_limit.return_value = True

        # Mock runtime manager so both stream and batch fail
        mock_mgr = MagicMock()
        async def broken_stream(*args, **kwargs):
            raise Exception("Stream error")
            yield
        mock_mgr.stream_response = broken_stream
        mock_mgr.generate_response = AsyncMock(side_effect=Exception("Batch error"))

        with patch("app.services.agent_service.usage_limit_service", mock_usage), \
             patch("app.services.agent_service.provider_runtime_manager", mock_mgr):
            res = await generation_node(state)

        final_ans = res.get("response", "")
        self.assertNotIn(secret_marker, final_ans, "Secret internal context marker must NEVER be exposed as answer")
        self.assertNotIn("Based on retrieved context:", final_ans, "Raw retrieved context fallback must not be returned")
        self.assertIn("unable to process", final_ans.lower())

    # =========================================================================
    # BUG-05: GENERAL CHAT ROUTING (SKIPS RETRIEVE NODE)
    # =========================================================================

    def test_BUG_05_general_queries_route_directly_to_generate(self):
        """
        Verify that general questions route directly to 'generate', NOT 'retrieve'.
        """
        general_queries = [
            "What is photosynthesis?",
            "Explain recursion in Python.",
            "How does HTTP middleware work?",
            "Why is the sky blue?"
        ]
        for q in general_queries:
            state = {
                "intent": IntentType.GENERAL.value,
                "rag_enabled": False,
                "attached_docs": [],
                "documents": [],
                "web_search": False,
                "query": q
            }
            routed_node = router(state)
            self.assertEqual(routed_node, "generate", f"Query '{q}' should route to 'generate', got '{routed_node}'")

    def test_BUG_05_document_and_search_queries_route_correctly(self):
        """
        Verify that document questions route to 'retrieve' and search questions route to 'search'.
        """
        doc_state = {
            "intent": IntentType.RAG.value,
            "rag_enabled": True,
            "attached_docs": ["doc.pdf"],
            "web_search": False
        }
        self.assertEqual(router(doc_state), "retrieve")

        search_state = {
            "intent": IntentType.SEARCH.value,
            "rag_enabled": False,
            "attached_docs": [],
            "web_search": True
        }
        self.assertEqual(router(search_state), "search")

    # =========================================================================
    # BUG-06: INTENT CLASSIFICATION TEST MATRIX
    # =========================================================================

    async def test_BUG_06_mandatory_intent_matrix(self):
        """
        Execute the exact mandatory intent test matrix required by CTO.
        """
        matrix = [
            ("find the bug in this code", IntentType.GENERAL),
            ("compare list and tuple in Python", IntentType.GENERAL),
            ("search the web for latest AI news", IntentType.SEARCH),
            ("find today's weather", IntentType.SEARCH),
            ("explain recursion", IntentType.GENERAL),
            ("summarize this attached PDF", IntentType.RAG),
            ("analyze this dataset", IntentType.ANALYTICS),
            ("generate an image of a sunset", IntentType.IMAGE_GEN),
        ]

        for query, expected_intent in matrix:
            detected = await IntentClassifierService.classify(query)
            self.assertEqual(
                detected,
                expected_intent,
                f"For query '{query}', expected {expected_intent.value} but got {detected.value}"
            )

    # =========================================================================
    # BUG-07: CONDITIONAL QUERY REWRITE
    # =========================================================================

    async def test_BUG_07_general_chat_does_not_invoke_query_rewrite(self):
        """
        Verify that general chat queries do NOT invoke QueryRewriteService.rewrite().
        """
        state = {
            "query": "How does binary search work?",
            "memory_enabled": False,
            "session_id": "test_session",
            "user_id": 1,
            "web_search": False,
            "rag_enabled": False,
            "intent": IntentType.GENERAL.value
        }

        mock_rewrite = AsyncMock()

        with patch("app.services.agent_service.QueryRewriteService.rewrite", mock_rewrite):
            res = await preprocessing_node(state)

        # Assert rewrite was NOT called
        mock_rewrite.assert_not_called()
        self.assertEqual(res["rewritten_query"], "How does binary search work?")

    async def test_BUG_07_search_and_rag_do_invoke_query_rewrite(self):
        """
        Verify that when web_search or RAG is active, QueryRewriteService.rewrite IS called.
        """
        state = {
            "query": "search the web for latest Python 3.14 release notes",
            "memory_enabled": False,
            "session_id": "test_session",
            "user_id": 1,
            "web_search": True,
            "rag_enabled": False,
            "intent": IntentType.SEARCH.value
        }

        mock_rewrite = AsyncMock(return_value="Python 3.14 release notes")

        with patch("app.services.agent_service.QueryRewriteService.rewrite", mock_rewrite):
            res = await preprocessing_node(state)

        mock_rewrite.assert_called_once()
        self.assertEqual(res["rewritten_query"], "Python 3.14 release notes")

    # =========================================================================
    # BUG-08: TEMPERATURE PROPAGATION
    # =========================================================================

    async def test_BUG_08_temperature_propagates_to_provider(self):
        """
        Verify that configured temperature (e.g. 0.2) in AgentState arrives at provider.stream_chat.
        """
        mock_provider = MagicMock()
        received_temp = []
        async def mock_stream(message, model=None, temperature=0.7, max_tokens=4096):
            received_temp.append(temperature)
            yield "Token"
        mock_provider.stream_chat = mock_stream

        with patch.dict(provider_runtime_manager.providers, {"openai": mock_provider}, clear=True), \
             patch("app.modules.provider_runtime.manager.provider_runtime_manager.provider_health_service.get_best_provider", AsyncMock(return_value="openai")):

            # Call stream_response with explicit temperature 0.2
            async for _ in provider_runtime_manager.stream_response("test prompt", temperature=0.2):
                pass

        self.assertEqual(received_temp, [0.2], "Configured temperature 0.2 must reach provider")

    # =========================================================================
    # BUG-10: PROVIDER CONFIGURATION & HEALTH REGISTRATION
    # =========================================================================

    def test_BUG_10_gemini_registered_in_health_and_valid_model(self):
        """
        Verify that gemini is registered in ProviderHealthService.providers and model name is valid.
        """
        self.assertIn("gemini", provider_health_service.providers, "gemini must be registered in ProviderHealthService")
        self.assertTrue(provider_health_service.is_available("gemini"), "gemini must be reported as available")
        self.assertNotIn("2.5", GEMINI_MODEL_NAME, "Gemini model name should be a released model (1.5 or 2.0)")


if __name__ == "__main__":
    unittest.main()
