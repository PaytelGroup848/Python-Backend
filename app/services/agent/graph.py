from __future__ import annotations

import logging
import re
import time
import uuid
from typing import Any, Optional

from langgraph.graph import StateGraph, END

from app.services.agent.prompts import GREETING_OPENERS
from app.services.agent.schemas import (
    AgentResponse,
    AgentState,
    IntentType,
    execute_with_retry,
)
from app.services.agent.services.context_builder import is_conversational_memory_query
from app.services.agent.nodes.preprocess_nodes import (
    assistant_runtime_node,
    cag_node,
    classify_node,
    preprocessing_node,
    planner_node,
)
from app.services.agent.nodes.retrieval_node import retrieval_node
from app.services.agent.nodes.analytics_node import analytics_node
from app.services.agent.nodes.search_node import search_node
from app.services.agent.nodes.finance_node import finance_node
from app.services.agent.nodes.generation_node import generation_node
from app.services.agent.nodes.image_gen_node import image_gen_node

logger = logging.getLogger("enterprise_agent")


# =========================================================
# ROUTER
# =========================================================

_NON_SEARCH_PREFIXES = (
    "write a ", "write code", "create a ", "build a ", "debug ", "fix this",
    "refactor ", "convert ", "translate ", "summarize ", "rewrite ",
)
_CASUAL_PHRASES = frozenset({
    "thank you", "thanks bro", "thanks a lot", "good job", "very nice",
    "nice one", "got it", "sounds good", "no problem", "ok bye",
    "samajh gaya", "theek hai", "thik hai", "bahut badhiya", "ok bro",
    "kya haal", "kya hal", "all good", "yes please", "no thanks",
})
_INFO_QUESTION_PATTERNS = (
    r"\b(what\s+is|what\s+are|who\s+is|who\s+are|where\s+is|when\s+was|why\s+does|why\s+is|how\s+does|how\s+do|how\s+to)\b",
    r"\b(explain|overview|benefits\s+of|advantages\s+of|difference\s+between|history\s+of|meaning\s+of|guide\s+to)\b",
    r"\b(kya\s+hai|kya\s+hota\s+hai|kaise\s+kaam|kaun\s+hai|kab\s+hua|kyu\s+hota)\b",
)


def _should_auto_search(query: str) -> bool:
    """Routes informational/knowledge queries through search_node for Perplexity-style sources & images."""
    if not query or not isinstance(query, str):
        return False
    normalized = query.strip().lower().rstrip("!.,? ")
    words = normalized.split()
    if not normalized or normalized in GREETING_OPENERS or normalized in _CASUAL_PHRASES or len(words) < 2:
        return False
    if normalized.startswith(_NON_SEARCH_PREFIXES) or "```" in query:
        return False
    if any(re.search(p, normalized) for p in _INFO_QUESTION_PATTERNS):
        return True
    return len(words) >= 2


def router(state: AgentState):
    if state.get("is_custom") and state.get("strict_rag"):
        return "retrieve"

    intent = state.get("intent")

    if intent in (IntentType.IMAGE_GEN.value, IntentType.IMAGE_EDIT.value):
        return "image_gen"

    if intent == IntentType.ANALYTICS.value:
        return "analytics"

    if intent == IntentType.FINANCE.value:
        return "finance"

    if intent == IntentType.SEARCH.value or state.get("web_search"):
        return "search"

    has_doc = bool(state.get("attached_docs") or state.get("documents"))

    # Conversational memory guard: route queries referencing past conversation history directly to generate
    if is_conversational_memory_query(state.get("query", "")) and not has_doc:
        return "generate"

    # Only route to retrieve if a document is attached or explicit RAG intent
    if has_doc or (intent == IntentType.RAG.value):
        return "retrieve"

    # Perplexity-style auto-search for informational General Chat queries (excluding greetings/code)
    if _should_auto_search(state.get("query", "")):
        return "search"

    return "generate"


# =========================================================
# BUILD GRAPH
# =========================================================

graph = StateGraph(AgentState)

graph.add_node("classify", classify_node)
graph.add_node("preprocess", preprocessing_node)
graph.add_node("assistant_runtime", assistant_runtime_node)
graph.add_node("cag", cag_node)
graph.add_node("planner", planner_node)
graph.add_node("retrieve", retrieval_node)
graph.add_node("analytics", analytics_node)
graph.add_node("search", search_node)
graph.add_node("generate", generation_node)
graph.add_node("image_gen", image_gen_node)
graph.add_node("finance", finance_node)

graph.set_entry_point("classify")

graph.add_edge("classify", "preprocess")
graph.add_edge("preprocess", "assistant_runtime")
graph.add_edge("assistant_runtime", "cag")
graph.add_edge("cag", "planner")

graph.add_conditional_edges(
    "planner",
    router,
    {
        "analytics": "analytics",
        "search": "search",
        "retrieve": "retrieve",
        "generate": "generate",
        "image_gen": "image_gen",
        "finance": "finance",
    }
)

graph.add_edge("finance", "generate")
graph.add_edge("analytics", "generate")
graph.add_edge("search", "generate")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)
graph.add_edge("image_gen", END)

agent = graph.compile()


# =========================================================
# RUNTIME
# =========================================================

class AgentRuntime:

    @staticmethod
    async def execute(
        query: str,
        session_id: str,
        user_id: int,
        assistant_id: int | None,
        user_role: str,
        user_department: str,
        aspect_ratio: str = "1024x1024",
        web_search: bool = False,
        stream_handler: Optional[Any] = None,
        attached_docs: Optional[list] = None
    ) -> AgentResponse:
        request_id = str(uuid.uuid4())
        started_at = time.time()
        logger.info(f"Agent execution started: {request_id}")

        state: AgentState = {
            "query": query,
            "rewritten_query": "",
            "session_id": session_id,
            "user_id": user_id,
            "assistant_id": assistant_id,
            "user_role": user_role,
            "user_department": user_department,
            "request_id": request_id,
            "intent": "",
            "language": "en",
            "system_prompt": "",
            "assistant_name": "",
            "assistant_code": "",
            "model_id": None,
            "temperature": 0.2,
            "top_p": 0.95,
            "max_tokens": 4000,
            "context_window": 8000,
            "memory_enabled": True,
            "rag_enabled": bool(attached_docs),
            "cag_enabled": False,
            "tool_calling_enabled": False,
            "is_custom": False,
            "strict_rag": False,
            "cag_hit": False,
            "cag_response": "",
            "memory_context": "",
            "plan": "",
            "context": "",
            "sources": [],
            "web_sources": [],
            "web_images": [],
            "web_search": web_search,
            "tool_result": {},
            "response": "",
            "aspect_ratio": aspect_ratio,
            "needs_general_knowledge": False,
            "stream_handler": stream_handler,
            "attached_docs": attached_docs or []
        }

        result = await execute_with_retry(
            agent.ainvoke,
            state
        )

        latency = int((time.time() - started_at) * 1000)
        logger.info(f"Agent completed: {request_id} | {latency}ms")

        return AgentResponse(
            response=result["response"],
            metadata={
                "request_id": request_id,
                "latency_ms": latency,
                "intent": result["intent"]
            }
        )


# =========================================================
# PUBLIC FUNCTION
# =========================================================

async def run_agent(
    query: str,
    session_id: str,
    user_id: int,
    assistant_id: int | None,
    user_role: str,
    user_department: str,
    aspect_ratio: str = "1024x1024",
    web_search: bool = False,
    stream_handler: Optional[Any] = None,
    attached_docs: Optional[list] = None
):
    result = await AgentRuntime.execute(
        query=query,
        session_id=session_id,
        user_id=user_id,
        assistant_id=assistant_id,
        user_role=user_role,
        user_department=user_department,
        aspect_ratio=aspect_ratio,
        web_search=web_search,
        stream_handler=stream_handler,
        attached_docs=attached_docs
    )

    return result.response
