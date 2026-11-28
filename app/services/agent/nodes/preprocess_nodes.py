from __future__ import annotations

import asyncio
import logging
import re

from app.db.database import AsyncSessionLocal
from app.modules.assistants.services.assistant_runtime_service import (
    assistant_runtime_service,
)
from app.modules.memory.services.cag_service import (
    cag_service,
)
from app.services.agent.schemas import AgentState, IntentType
from app.services.agent.services.classifier import IntentClassifierService
from app.services.agent.services.context_builder import (
    GENERAL_CHAT_MASTER_PROMPT,
    is_conversational_memory_query,
)
from app.services.agent.services.memory import SemanticMemoryService
from app.services.agent.services.query_planner import (
    PlanningService,
    QueryRewriteService,
)
from app.services.agent.services.tools import LanguagePipeline

logger = logging.getLogger("enterprise_agent")


async def assistant_runtime_node(state: AgentState):
    if state["assistant_id"] is None:
        return {
            **state,
            "system_prompt": GENERAL_CHAT_MASTER_PROMPT,
            "assistant_name": "General Chat",
            "assistant_code": "GENERAL",
            "model_id": None,
            "temperature": 0.65,
            "top_p": 0.90,
            "max_tokens": 4000,
            "context_window": 8000,
            "memory_enabled": True,
            "rag_enabled": False,
            "cag_enabled": False,
            "tool_calling_enabled": False,
            "is_custom": False,
            "strict_rag": False,
        }

    async with AsyncSessionLocal() as db:
        runtime = await (
            assistant_runtime_service.load_runtime(
                db=db,
                assistant_id=state["assistant_id"],
                user_id=state.get("user_id"),
            )
        )

    return {
        **state,
        "system_prompt": runtime.system_prompt or "",
        "assistant_name": runtime.assistant_name,
        "assistant_code": runtime.assistant_code,
        "model_id": runtime.model_id,
        "temperature": float(runtime.temperature) if runtime.temperature is not None else 0.2,
        "top_p": float(runtime.top_p) if runtime.top_p is not None else 0.95,
        "max_tokens": int(runtime.max_tokens) if runtime.max_tokens is not None else 4000,
        "context_window": int(runtime.context_window) if runtime.context_window is not None else 8000,
        "memory_enabled": bool(runtime.memory_enabled) if runtime.memory_enabled is not None else True,
        "rag_enabled": bool(runtime.rag_enabled) if runtime.rag_enabled is not None else True,
        "cag_enabled": runtime.cag_enabled,
        "tool_calling_enabled": runtime.tool_calling_enabled,
        "is_custom": runtime.is_custom,
        "strict_rag": runtime.strict_rag,
    }


async def cag_node(state: AgentState):
    assistant_id = state.get("assistant_id")
    if not state["cag_enabled"] or assistant_id is None:
        return state

    cached = await (
        cag_service.get_response(
            assistant_id=assistant_id,
            query=state["query"]
        )
    )

    if not cached:
        logger.info(f"CAG MISS: {state['query']}")
        return state

    logger.info(f"CAG HIT: {state['query']}")

    return {
        **state,
        "cag_hit": True,
        "cag_response": cached["response"],
        "response": cached["response"]
    }


async def classify_node(state: AgentState):
    intent = await IntentClassifierService.classify(state["query"])
    return {
        **state,
        "intent": intent.value
    }


async def preprocessing_node(state: AgentState):
    query, language = await LanguagePipeline.process_input(state["query"])

    if state["memory_enabled"]:
        memory_task = SemanticMemoryService.load_memory(state["session_id"])
    else:
        memory_task = asyncio.sleep(0, result="")

    is_web_search = bool(state.get("web_search", False))
    clean_query = query
    q_lower = query.lower()
    if "[web search]" in q_lower or q_lower.startswith("/search") or "--search" in q_lower:
        is_web_search = True
        clean_query = re.sub(r"\[web search\]", "", clean_query, flags=re.IGNORECASE)
        clean_query = re.sub(r"^\/search\s*", "", clean_query, flags=re.IGNORECASE)
        clean_query = re.sub(r"--search", "", clean_query, flags=re.IGNORECASE).strip()

    is_conv_memory = is_conversational_memory_query(clean_query)

    needs_rewrite = (
        not is_conv_memory
        and (
            is_web_search
            or bool(state.get("rag_enabled", False))
            or state.get("intent") in (IntentType.SEARCH.value, IntentType.RAG.value)
        )
    )

    if needs_rewrite:
        rewrite_task = QueryRewriteService.rewrite(
            query=clean_query,
            user_id=state["user_id"]
        )
        memory, rewritten = await asyncio.gather(
            memory_task,
            rewrite_task
        )
    else:
        memory = await memory_task
        rewritten = clean_query

    return {
        **state,
        "query": clean_query,
        "language": language,
        "memory_context": memory,
        "rewritten_query": rewritten,
        "web_search": is_web_search,
    }


async def planner_node(state: AgentState):
    if state["intent"] != IntentType.MULTISTEP.value:
        return {
            **state,
            "plan": ""
        }

    plan = await PlanningService.create_plan(
        query=state["query"],
        user_id=state["user_id"]
    )

    return {
        **state,
        "plan": plan
    }
