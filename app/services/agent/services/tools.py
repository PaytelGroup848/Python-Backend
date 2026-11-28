from __future__ import annotations

import logging
import re
from app.db.database import AsyncSessionLocal
from app.services.agent.schemas import ToolResult, RetrievalResult
from app.services.language_service import detect_language_and_script
from app.services.tool_service import get_system_stats, search_documents_tool
from app.modules.retrieval_runtime.services.rag_service import retrieve_context

logger = logging.getLogger("enterprise_agent")


class AnalyticsService:

    @staticmethod
    async def execute() -> ToolResult:
        async with AsyncSessionLocal() as db:
            stats = await get_system_stats(db)
            return ToolResult(
                success=True,
                data=stats
            )


class DocumentSearchService:

    @staticmethod
    async def execute(
        query: str,
        role: str,
        department: str
    ) -> ToolResult:
        try:
            async with AsyncSessionLocal() as db:
                docs = await search_documents_tool(
                    db=db,
                    query=query,
                    user_role=role,
                    user_department=department
                )
                return ToolResult(
                    success=True,
                    data={"documents": docs}
                )
        except Exception as e:
            logger.warning(f"Document search execution failed: {e}")
            return ToolResult(
                success=True,
                data={"documents": []}
            )


class RetrievalService:

    @staticmethod
    async def retrieve(
        query: str,
        assistant_id: int,
        role: str,
        department: str
    ) -> RetrievalResult:
        async with AsyncSessionLocal() as db:
            result = await retrieve_context(
                db=db,
                query=query,
                assistant_id=assistant_id,
                user_role=role,
                user_department=department
            )

            if result.get("needs_general_knowledge"):
                return RetrievalResult(
                    needs_general_knowledge=True,
                    message=result["message"]
                )

            return RetrievalResult(
                context=result.get("context", ""),
                sources=result.get("sources", [])
            )


class LanguagePipeline:
    """
    Enterprise Native Multilingual Pipeline:
    Zero external translation overhead. The LLM natively reasons and responds
    directly in the language and script requested by the user, governed by the
    authoritative central ContextBuilderService language directive.
    """

    @staticmethod
    async def process_input(query: str):
        detected = detect_language_and_script(query)
        return query, detected.get("type", "english")

    @staticmethod
    async def process_output(response: str, language: str = "auto"):
        if not response:
            return ""
        cleaned = re.sub(r'^\s*ANSWER\s*\([^)]*\)\s*:\s*', '', response, flags=re.IGNORECASE)
        return cleaned.strip() if cleaned else response
