from __future__ import annotations

from app.modules.memory.services.memory_service import memory_service
from app.services.suggestion_service import clean_legacy_memory_text
from app.services.agent.schemas import MAX_MEMORY_MESSAGES


class SemanticMemoryService:

    @staticmethod
    async def load_memory(session_id: str) -> str:
        memory = await memory_service.get_memory(session_id)
        memory = memory[-MAX_MEMORY_MESSAGES:]

        formatted_lines = []
        for m in memory:
            content = m.get("content", "")
            if m.get("role") == "assistant":
                content = clean_legacy_memory_text(content)
            formatted_lines.append(f"{m['role']}: {content}")

        return "\n".join(formatted_lines)
