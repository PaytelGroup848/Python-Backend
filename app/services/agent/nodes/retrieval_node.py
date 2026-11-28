from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Optional

from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.models.knowledge_base_document import KnowledgeBaseDocument
from app.services.agent.schemas import AgentState
from app.services.agent.services.tools import RetrievalService
from app.services.document_parser_service import parse_document
from app.services.web_search_service import web_search_service
from app.shared.redis.client import redis_client

logger = logging.getLogger("enterprise_agent")

_IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp"})


async def _retrieve_kb_context(state: AgentState) -> tuple[str, list[Any], bool, str]:
    assistant_id = state.get("assistant_id")
    if not state.get("rag_enabled") or assistant_id is None:
        return "", [], False, ""

    query_to_use = (state.get("rewritten_query") or "").strip() or state["query"]
    result = await RetrievalService.retrieve(
        query=query_to_use,
        assistant_id=assistant_id,
        role=state["user_role"],
        department=state["user_department"],
    )

    res_context = result.get("context", "") if isinstance(result, dict) else getattr(result, "context", "")
    if not res_context and state["query"] != query_to_use:
        logger.info("Rewritten query returned no results. Retrying retrieval with raw user query.")
        result = await RetrievalService.retrieve(
            query=state["query"],
            assistant_id=assistant_id,
            role=state["user_role"],
            department=state["user_department"],
        )
        res_context = result.get("context", "") if isinstance(result, dict) else getattr(result, "context", "")

    res_sources = list(result.get("sources", [])) if isinstance(result, dict) else list(getattr(result, "sources", []))
    needs_gk = result.get("needs_general_knowledge", False) if isinstance(result, dict) else getattr(result, "needs_general_knowledge", False)
    res_msg = result.get("message", "") if isinstance(result, dict) else getattr(result, "message", "")
    return res_context, res_sources, needs_gk, res_msg


async def _resolve_attached_filename(state: AgentState) -> Optional[str]:
    attached = state.get("attached_docs") or state.get("documents")
    if attached:
        if isinstance(attached, list) and attached:
            return str(attached[0])
        if isinstance(attached, str):
            return attached

    session_id = str(state.get("session_id", "") or "")
    if not session_id:
        return None

    raw_conv = await redis_client.get(f"conversation_pdf:{session_id}")
    if not raw_conv:
        return None
    try:
        conv_docs = json.loads(raw_conv)
        if isinstance(conv_docs, list) and conv_docs:
            return str(conv_docs[0])
        if isinstance(conv_docs, str):
            return conv_docs
    except Exception:
        return raw_conv
    return None


async def _load_attached_doc_context(state: AgentState, res_sources: list[Any]) -> str:
    try:
        filename = await _resolve_attached_filename(state)
        if not filename:
            return ""

        async with AsyncSessionLocal() as db:
            kb_res = await db.execute(
                select(KnowledgeBaseDocument)
                .filter(KnowledgeBaseDocument.file_name == filename)
                .order_by(KnowledgeBaseDocument.id.desc())
                .limit(1)
            )
            kb_doc = kb_res.scalar_one_or_none()

        if not kb_doc or not kb_doc.file_path:
            return ""

        ext = os.path.splitext(kb_doc.file_path)[1].lower()
        if ext in _IMAGE_EXTENSIONS:
            from app.services.vision_service import VisionService

            logger.info(f"Analyzing attached image with Multimodal Vision (Pixtral): {kb_doc.file_path}")
            vision_analysis = await VisionService.analyze_image(
                file_path=kb_doc.file_path,
                prompt=state.get("query"),
            )
            _append_source_once(res_sources, filename)
            if vision_analysis:
                return (
                    f"=== USER ATTACHED IMAGE ANALYSIS ({filename}) ===\n"
                    f"Visual Understanding & Inspection Details:\n{vision_analysis}\n"
                    f"=== END OF IMAGE ANALYSIS ==="
                )
            return f"=== USER ATTACHED IMAGE ({filename}) ===\n[Image attached]\n=== END ==="

        pages = await parse_document(kb_doc.file_path)
        if not pages:
            return ""

        text_parts = [
            f"[Page {p.get('page_number', i + 1)}]\n{txt}"
            for i, p in enumerate(pages[:50])
            if (txt := (p.get("text") or "").strip())
        ]
        full_doc_text = "\n\n".join(text_parts)
        if len(full_doc_text) > 12000:
            full_doc_text = full_doc_text[:12000] + "\n\n[... Remaining pages omitted for length ...]"
        if not full_doc_text:
            return ""

        _append_source_once(res_sources, filename)
        return f"=== USER ATTACHED DOCUMENT ({filename}) ===\n{full_doc_text}\n=== END OF ATTACHED DOCUMENT ==="
    except Exception as exc:
        logger.warning(f"Error loading attached document context: {exc}")
        return ""


def _append_source_once(res_sources: list[Any], filename: str) -> None:
    if not any(isinstance(s, dict) and s.get("source_file") == filename for s in res_sources):
        res_sources.append({"source_file": filename, "page_number": 1})


async def _run_web_fallback(state: AgentState) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    try:
        query_to_search = (state.get("rewritten_query") or "").strip() or state["query"]
        payload = await asyncio.to_thread(
            web_search_service.search_with_images,
            query_to_search,
            max_results=8,
            max_images=8,
        )
        web_sources = payload.get("sources", [])
        web_images = payload.get("images", [])
        if not web_sources and not web_images:
            return "", [], []

        stream_handler = state.get("stream_handler")
        if stream_handler is not None:
            try:
                await stream_handler({
                    "type": "sources",
                    "sources": web_sources,
                    "images": web_images,
                })
            except Exception as exc:
                logger.warning(f"Failed to stream fallback sources event: {exc}")

        web_ctx = web_search_service.format_search_context(web_sources) if web_sources else ""
        return web_ctx, web_sources, web_images
    except Exception as exc:
        logger.warning(f"Web search in retrieval_node failed: {exc}")
        return "", [], []


async def retrieval_node(state: AgentState):
    """Retrieves knowledge base context, attached document contents, and live web fallback."""
    res_context, res_sources, res_needs_gk, res_msg = await _retrieve_kb_context(state)

    assistant_id = state.get("assistant_id")
    if assistant_id is not None:
        from app.models.assistant import Assistant
        from app.modules.mini_ai.repository import mini_ai_repository
        async with AsyncSessionLocal() as inv_db:
            meta_res = await inv_db.execute(
                select(Assistant.is_custom, Assistant.strict_rag).where(
                    Assistant.id == int(assistant_id)
                )
            )
            meta_row = meta_res.first()
            inventory_ctx = await mini_ai_repository.get_custom_kb_inventory(
                inv_db, int(assistant_id)
            )
        if inventory_ctx:
            res_context = f"{inventory_ctx}\n\n{res_context}" if res_context else inventory_ctx
            res_needs_gk = False
        if meta_row and meta_row[0] and meta_row[1]:
            res_needs_gk = False
            strict_policy = (
                "=== STRICT MINI AI GROUNDING RULE ===\n"
                "You are a dedicated Custom Knowledge Bot with STRICT GROUNDING enabled.\n"
                "1. If the user greets you (hi/hello/namaste) OR asks what dataset, files, or knowledge you have "
                "(e.g. 'kaunsa dataset uploaded hai', 'kis chij ki knowledge hai', 'what files/data do you have'), "
                "ALWAYS answer directly using the exact file names, chunk counts, and sample preview in MY MINI AI KNOWLEDGE INVENTORY above.\n"
                "2. For all other factual questions, answer ONLY using facts explicitly present in the retrieved knowledge or inventory above.\n"
                "3. ONLY if the answer is completely absent from both MY MINI AI KNOWLEDGE INVENTORY and retrieved knowledge above, reply ONLY with:\n"
                "\"Mere uploaded dataset me iski jaankari nahi hai. General sawalon ke liye General Chat use karein, ya is Mini AI me iska data add karein.\"\n"
                "=== END OF STRICT RULE ==="
            )
            res_context = f"{res_context}\n\n{strict_policy}" if res_context else strict_policy

    doc_context = await _load_attached_doc_context(state, res_sources)
    if doc_context:
        res_context = f"{doc_context}\n\n{res_context}" if res_context else doc_context

    web_sources = list(state.get("web_sources") or [])
    web_images = list(state.get("web_images") or [])
    if state.get("web_search") or (res_needs_gk and state.get("query")):
        web_ctx, fetched_sources, fetched_images = await _run_web_fallback(state)
        if web_ctx or fetched_images:
            res_context = f"{res_context}\n\n{web_ctx}" if (res_context and web_ctx) else (web_ctx or res_context)
            web_sources = fetched_sources
            web_images = fetched_images
            res_needs_gk = False

    return {
        **state,
        "context": res_context,
        "sources": res_sources,
        "web_sources": web_sources,
        "web_images": web_images,
        "needs_general_knowledge": res_needs_gk,
        "response": res_msg,
    }
