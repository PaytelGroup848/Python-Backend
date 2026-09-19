import pytest
from unittest.mock import AsyncMock, patch
from app.services.agent_service import SemanticMemoryService
from app.services.suggestion_service import extract_and_normalize_suggestions


@pytest.mark.asyncio
async def test_full_memory_lifecycle_turn1_to_turn2():
    """
    Verifies that Turn 1 assistant suggestions are NEVER persisted into semantic memory,
    and Turn 2 load_memory contains ONLY the primary response.
    """
    mock_storage = []

    async def mock_save_memory(session_id, role, message):
        mock_storage.append({"role": role, "content": message})

    async def mock_get_memory(session_id):
        return list(mock_storage)

    with patch("app.modules.memory.services.memory_service.memory_service.save_memory", side_effect=mock_save_memory), \
         patch("app.modules.memory.services.memory_service.memory_service.get_memory", side_effect=mock_get_memory):

        # Turn 1: User asks question, LLM outputs response with suggestions
        user_query = "What is the difference between list and tuple?"
        llm_raw_response = (
            "List is mutable and tuple is immutable in Python.\n\n"
            "```python\n"
            "my_list = [1, 2]\n"
            "my_tuple = (1, 2)\n"
            "```\n\n"
            "**💡 Suggestions:**\n"
            "- Suggestion 1: When should I use tuple?\n"
            "- Suggestion 2: Explain memory efficiency\n"
        )

        clean_body, suggestions = extract_and_normalize_suggestions(llm_raw_response)
        assert len(suggestions) == 2
        assert "When should I use tuple?" in suggestions
        assert "Explain memory efficiency" in suggestions

        # Save to memory (simulating generation_node memory isolation)
        await mock_save_memory("session-123", role="user", message=user_query)
        await mock_save_memory("session-123", role="assistant", message=clean_body)

        # Assert: Persisted memory contains assistant answer with code, but ZERO suggestions
        persisted_assistant_msg = next(m["content"] for m in mock_storage if m["role"] == "assistant")
        assert "List is mutable and tuple is immutable" in persisted_assistant_msg
        assert "my_list = [1, 2]" in persisted_assistant_msg
        assert "Suggestions" not in persisted_assistant_msg
        assert "When should I use tuple?" not in persisted_assistant_msg

        # Turn 2: load_memory for next turn prompt context
        loaded_memory = await SemanticMemoryService.load_memory("session-123")

        # Invariant #3: Old suggestions NEVER leak into Turn 2 prompt context
        assert "user: What is the difference between list and tuple?" in loaded_memory
        assert "assistant: List is mutable and tuple is immutable" in loaded_memory
        assert "Suggestions" not in loaded_memory


@pytest.mark.asyncio
async def test_legacy_memory_cleaning_in_load_memory():
    """
    Verifies that historical legacy sessions stored in Redis/DB with raw suggestions blocks
    are cleanly stripped by SemanticMemoryService.load_memory without corrupting legitimate text.
    """
    historical_data = [
        {"role": "user", "content": "How do I use Python?"},
        {
            "role": "assistant",
            "content": (
                "Python is versatile and easy to learn.\n"
                "Suggestions are helpful for beginners.\n\n"
                "**💡 Suggestions:**\n"
                "- Old suggestion 1\n"
                "- Old suggestion 2"
            )
        }
    ]

    with patch("app.modules.memory.services.memory_service.memory_service.get_memory", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = historical_data

        memory_prompt = await SemanticMemoryService.load_memory("legacy-session")

        # Legitimate body prose containing the word 'Suggestions' is preserved
        assert "Suggestions are helpful for beginners." in memory_prompt
        assert "Python is versatile and easy to learn." in memory_prompt

        # Trailing suggestions block is stripped
        assert "Old suggestion 1" not in memory_prompt
        assert "Old suggestion 2" not in memory_prompt
        assert "**💡 Suggestions:**" not in memory_prompt
