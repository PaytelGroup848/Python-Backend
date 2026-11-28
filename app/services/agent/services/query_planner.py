from __future__ import annotations

import logging
from app.modules.provider_runtime.manager.provider_runtime_manager import (
    provider_runtime_manager,
)

logger = logging.getLogger("enterprise_agent")


class QueryRewriteService:

    @staticmethod
    async def rewrite(query: str, user_id: int) -> str:
        prompt = f"""
Rewrite this query into a concise search query (maximum 8 keywords).
Do NOT include explanations, introduction, quotes, or markdown. Output ONLY the search query keywords.

USER QUERY:
{query}

SEARCH QUERY:
"""
        try:
            response = await provider_runtime_manager.generate_response(
                prompt=prompt,
                user_id=user_id,
                temperature=0.1
            )
            raw = response["response"].strip()
            lines = [
                l.strip().strip('"\'*')
                for l in raw.split("\n")
                if l.strip() and not l.lower().startswith(("here", "optimized", "note", "---", "#"))
            ]
            candidate = lines[0] if lines else raw.strip('"\'*')
            if len(candidate) > 120 or not candidate:
                return query.strip()
            return candidate
        except Exception as exc:
            logger.warning(f"Query rewrite failed (using raw query): {exc}")
            return query


class PlanningService:

    @staticmethod
    async def create_plan(query: str, user_id: int) -> str:
        prompt = f"""
                    Break this request into concise execution steps.

                    REQUEST:
                    {query}

                    STEPS:
                """

        response = await provider_runtime_manager.generate_response(
            prompt=prompt,
            user_id=user_id,
            temperature=0.2
        )

        return response["response"]
