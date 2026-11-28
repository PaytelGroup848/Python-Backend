from __future__ import annotations

import logging
from typing import Optional

from app.db.database import AsyncSessionLocal
from app.modules.memory.services.cag_service import cag_service
from app.modules.memory.services.memory_service import memory_service
from app.modules.provider_runtime.manager.provider_runtime_manager import (
    provider_runtime_manager,
)
from app.modules.usage.services.usage_limit_service import usage_limit_service
from app.services.agent.schemas import AgentState, StreamHandler
from app.services.agent.services.context_builder import ContextBuilderService
from app.services.agent.services.tools import LanguagePipeline
from app.services.suggestion_service import extract_and_normalize_suggestions

logger = logging.getLogger("enterprise_agent")

_FALLBACK_ERROR_MESSAGE = "I am temporarily unable to process your request. Please try again shortly."
_WEB_CITATION_INSTRUCTION = (
    "INSTRUCTION: You have real-time live web search results above. "
    "Synthesize and summarize the actual facts, headlines, figures, and key takeaways directly from those results. "
    "NEVER say 'I do not have access to real-time data' or 'I cannot provide live updates' when search results are provided above. "
    "Cite your factual statements with inline citation numbers like [1], [2] corresponding to the search results above."
)


async def _emit_chunk(stream_handler: Optional[StreamHandler], content: str) -> None:
    if stream_handler is None:
        return
    try:
        await stream_handler({"type": "chunk", "content": content})
    except Exception as exc:
        logger.warning(f"Stream callback error: {exc}")


def _resolve_temperature(raw_temp: object) -> float:
    if not isinstance(raw_temp, (int, float, str)):
        return 0.65
    try:
        return float(raw_temp)
    except (ValueError, TypeError):
        return 0.65


async def _generate_batch_fallback(final_prompt: str, user_id: int, temperature: float) -> str:
    try:
        response = await provider_runtime_manager.generate_response(
            prompt=final_prompt,
            user_id=user_id,
            temperature=temperature,
            stream=False,
        )
        return response.get("response", "") if isinstance(response, dict) else str(response)
    except Exception as exc:
        logger.error(f"Batch/direct generation failed: {exc}")
        return _FALLBACK_ERROR_MESSAGE


async def _generate_response_text(
    chat_messages: list[dict[str, str]],
    final_prompt: str,
    user_id: int,
    temperature: float,
    stream_handler: Optional[StreamHandler],
) -> str:
    if stream_handler is None:
        return await _generate_batch_fallback(final_prompt, user_id, temperature)

    collected_chunks: list[str] = []
    try:
        async for chunk in provider_runtime_manager.stream_response(chat_messages, temperature=temperature):
            if chunk:
                collected_chunks.append(chunk)
                await _emit_chunk(stream_handler, chunk)
        return "".join(collected_chunks)
    except Exception as exc:
        logger.warning(f"Streaming provider error, falling back to batch: {exc}")
        fallback_text = await _generate_batch_fallback(final_prompt, user_id, temperature)
        if not collected_chunks:
            await _emit_chunk(stream_handler, fallback_text)
        return fallback_text


def _build_web_sources_suffix(web_sources: list, current_response: str) -> str:
    if not web_sources or not isinstance(web_sources, list) or "**🌐 Sources:**" in current_response:
        return ""
    links = [
        f"[{i}] [{ws.get('title') or f'Source {i}'}]({ws.get('url') or '#'})"
        for i, ws in enumerate(web_sources, start=1)
    ]
    return "\n\n**🌐 Sources:**\n" + "\n".join(links) if links else ""


def _build_doc_citations_suffix(sources_list: list, context: str, current_response: str) -> str:
    if not sources_list or not isinstance(sources_list, list) or not context:
        return ""
    pills: list[str] = []
    seen: set[str] = set()
    for src in sources_list:
        if isinstance(src, dict):
            f_name = src.get("source_file", "Document")
            p_num = src.get("page_number")
            pill = f"`📄 {f_name}{' (Page ' + str(p_num) + ')' if p_num else ''}`"
        else:
            pill = f"`📄 {src}`"
        if pill not in seen:
            seen.add(pill)
            pills.append(pill)

    if not pills or pills[0] in current_response:
        return ""
    return "\n\n**📌 Documents:**\n" + "  ".join(pills)


async def _persist_cag_and_memory(state: AgentState, final_response: str) -> None:
    assistant_id = state.get("assistant_id")
    if state.get("cag_enabled") and assistant_id is not None:
        await cag_service.save_response(
            assistant_id=assistant_id,
            query=state["query"],
            response=final_response,
        )
        logger.info(f"CAG SAVE: {state['query']}")

    if not state.get("memory_enabled"):
        return

    try:
        clean_content, _ = extract_and_normalize_suggestions(final_response)
    except Exception as exc:
        logger.warning(f"suggestion_parser_failed session_id={state.get('session_id')}: {exc}")
        clean_content = final_response

    await memory_service.save_memory(session_id=state["session_id"], role="user", message=state["query"])
    await memory_service.save_memory(session_id=state["session_id"], role="assistant", message=clean_content)


async def generation_node(state: AgentState):
    """Generates, streams, cites, and persists the final assistant response."""
    if state.get("cag_hit"):
        return state

    asst_code = str(state.get("assistant_code") or "").lower()
    allow_external = (
        asst_code in ("", "general", "coder")
        or "code" in asst_code
        or "general" in asst_code
        or not state.get("assistant_id")
    )
    if state.get("needs_general_knowledge") and not allow_external:
        return state

    async with AsyncSessionLocal() as db:
        if not await usage_limit_service.check_usage_limit(db, user_id=state["user_id"]):
            raise Exception("Plan limit exceeded")

    web_sources = state.get("web_sources") or []
    citation_instr = (
        _WEB_CITATION_INSTRUCTION
        if web_sources or "REAL-TIME LIVE WEB SEARCH RESULTS" in state.get("context", "")
        else ""
    )

    chat_messages = ContextBuilderService.build_chat_messages(
        query=state["query"],
        system_prompt=state.get("system_prompt", ""),
        memory=state.get("memory_context", ""),
        context=state.get("context", ""),
        tool_result=state.get("tool_result", {}),
        plan=state.get("plan", ""),
        web_citation_instr=citation_instr,
        max_total_chars=36000,
    )
    final_prompt = ContextBuilderService.build_prompt(
        query=state["query"],
        system_prompt=state.get("system_prompt", ""),
        memory=state.get("memory_context", ""),
        context=state.get("context", ""),
        tool_result=state.get("tool_result", {}),
        plan=state.get("plan", ""),
        web_citation_instr=citation_instr,
        max_total_chars=36000,
    )

    stream_handler = state.get("stream_handler")
    temperature = _resolve_temperature(state.get("temperature"))
    final_response = await _generate_response_text(
        chat_messages, final_prompt, state["user_id"], temperature, stream_handler
    )

    for suffix in (
        _build_web_sources_suffix(web_sources, final_response),
        _build_doc_citations_suffix(state.get("sources", []), state.get("context", ""), final_response),
    ):
        if suffix:
            final_response += suffix
            await _emit_chunk(stream_handler, suffix)

    final_response = await LanguagePipeline.process_output(final_response, state["language"])
    await _persist_cag_and_memory(state, final_response)

    return {**state, "response": final_response}
