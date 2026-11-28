from __future__ import annotations

import asyncio
import logging

from app.services.agent.schemas import AgentState
from app.services.agent.services.tools import DocumentSearchService
from app.services.web_search_service import web_search_service

logger = logging.getLogger("enterprise_agent")


async def search_node(state: AgentState):
    """Executes internal document search and live web + image search, streaming structured sources."""
    query = (state.get("rewritten_query") or "").strip() or state["query"]

    result = await DocumentSearchService.execute(
        query=query,
        role=state["user_role"],
        department=state["user_department"],
    )

    search_payload = {"sources": [], "images": []}
    try:
        search_payload = await asyncio.to_thread(
            web_search_service.search_with_images,
            query,
            max_results=8,
            max_images=8,
        )
    except Exception as exc:
        logger.warning(f"Web search in search_node error: {exc}")

    web_sources = search_payload.get("sources", [])
    web_images = search_payload.get("images", [])
    web_context = web_search_service.format_search_context(web_sources) if web_sources else ""

    stream_handler = state.get("stream_handler")
    if stream_handler is not None and (web_sources or web_images):
        try:
            await stream_handler({
                "type": "sources",
                "sources": web_sources,
                "images": web_images,
            })
        except Exception as exc:
            logger.warning(f"Failed to stream structured sources event: {exc}")

    current_context = state.get("context", "")
    combined_context = (
        f"{current_context}\n\n{web_context}".strip()
        if current_context and web_context
        else (web_context or current_context)
    )

    tool_data = dict(result.data) if hasattr(result, "data") else {}
    if web_sources:
        tool_data["web_search"] = web_sources

    return {
        **state,
        "context": combined_context,
        "tool_result": tool_data,
        "web_sources": web_sources,
        "web_images": web_images,
    }
