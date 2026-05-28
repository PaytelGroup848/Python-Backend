from __future__ import annotations

import asyncio
import logging
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END

from app.db.database import AsyncSessionLocal

from app.modules.chat.services.llm_manager import (
    llm_manager
)

from app.modules.chat.services.rag_service import (
    retrieve_context
)

from app.modules.chat.services.memory_service import (
    memory_service
)

from app.services.language_service import (
    detect_language,
    translate_response,
    translate_to_english
)

from app.services.tool_service import (
    get_system_stats,
    search_documents_tool
)

# =========================================================
# LOGGING
# =========================================================

logger = logging.getLogger("enterprise_agent")

# =========================================================
# CONFIG
# =========================================================

MAX_MEMORY_MESSAGES = 6
REQUEST_TIMEOUT = 30
RETRY_ATTEMPTS = 2

# =========================================================
# ENUMS
# =========================================================

class IntentType(str, Enum):
    GENERAL = "general"
    RAG = "rag"
    SEARCH = "search"
    ANALYTICS = "analytics"
    MULTISTEP = "multistep"


# =========================================================
# STRUCTURED MODELS
# =========================================================

class RetrievalResult(BaseModel):
    context: str = ""
    sources: List[dict] = Field(default_factory=list)
    needs_general_knowledge: bool = False
    message: str = ""


class ToolResult(BaseModel):
    success: bool = True
    data: Dict[str, Any] = Field(default_factory=dict)


class ExecutionMetadata(BaseModel):
    request_id: str
    started_at: float
    latency_ms: Optional[int] = None


class AgentResponse(BaseModel):
    response: str
    metadata: Dict[str, Any]


# =========================================================
# AGENT STATE
# =========================================================

class AgentState(TypedDict):

    # core request
    query: str
    rewritten_query: str

    # user
    session_id: str
    user_id: int
    user_role: str
    user_department: str

    # runtime
    request_id: str
    intent: str
    language: str

    # execution
    memory_context: str
    plan: str

    # retrieval
    context: str
    sources: list

    # tools
    tool_result: dict

    # generation
    response: str

    # metadata
    needs_general_knowledge: bool


# =========================================================
# RETRY + TIMEOUT WRAPPER
# =========================================================

async def execute_with_retry(
    coro,
    retries: int = RETRY_ATTEMPTS,
    timeout: int = REQUEST_TIMEOUT
):

    last_error = None

    for attempt in range(retries):

        try:

            return await asyncio.wait_for(
                coro,
                timeout=timeout
            )

        except Exception as e:

            last_error = e

            logger.exception(
                f"Retry attempt failed: {attempt + 1}"
            )

            await asyncio.sleep(1)

    raise last_error


# =========================================================
# INTENT CLASSIFIER
# =========================================================

class IntentClassifierService:

    @staticmethod
    async def classify(query: str) -> IntentType:

        q = query.lower()

        # lightweight deterministic routing first

        analytics_terms = [
            "analytics",
            "stats",
            "metrics",
            "dashboard",
            "usage"
        ]

        search_terms = [
            "find",
            "search",
            "lookup"
        ]

        rag_terms = [
            "document",
            "policy",
            "pdf",
            "report",
            "contract"
        ]

        multistep_terms = [
            "analyze",
            "compare",
            "review",
            "generate plan",
            "summarize all"
        ]

        if any(x in q for x in analytics_terms):
            return IntentType.ANALYTICS

        if any(x in q for x in search_terms):
            return IntentType.SEARCH

        if any(x in q for x in multistep_terms):
            return IntentType.MULTISTEP

        if any(x in q for x in rag_terms):
            return IntentType.RAG

        return IntentType.GENERAL


# =========================================================
# MEMORY SERVICE
# =========================================================

class SemanticMemoryService:

    @staticmethod
    async def load_memory(
        session_id: str
    ) -> str:

       
        memory = await memory_service.get_memory(
            session_id
        )

        memory = memory[-MAX_MEMORY_MESSAGES:]



        formatted = "\n".join(
            [
                f"{m['role']}: {m['content']}"
                for m in memory
            ]
        )

        return formatted


# =========================================================
# QUERY REWRITER
# =========================================================

class QueryRewriteService:

    @staticmethod
    async def rewrite(query: str) -> str:

        prompt = f"""
Rewrite this query into an optimized semantic search query.

USER QUERY:
{query}

OPTIMIZED QUERY:
"""

        response = await llm_manager.generate_response(
            prompt=prompt,
            user_id=0,
            temperature=0.1
        )

        return response["response"].strip()


# =========================================================
# PLANNER SERVICE
# =========================================================

class PlanningService:

    @staticmethod
    async def create_plan(query: str) -> str:

        prompt = f"""
Break this request into concise execution steps.

REQUEST:
{query}

STEPS:
"""

        response = await llm_manager.generate_response(
            prompt=prompt,
            user_id=0,
            temperature=0.2
        )

        return response["response"]


# =========================================================
# CONTEXT BUILDER
# =========================================================

class ContextBuilderService:

    @staticmethod
    def sanitize_context(context: str) -> str:

        blocked = [
            "ignore previous instructions",
            "reveal system prompt",
            "bypass security"
        ]

        lower = context.lower()

        for item in blocked:

            lower = lower.replace(item, "")

        return lower

    @staticmethod
    def build(
        memory: str,
        context: str,
        tool_result: dict,
        plan: str
    ) -> str:

        context = ContextBuilderService.sanitize_context(
            context
        )

        return f"""
You are an enterprise AI platform assistant.

Execution Plan:
{plan}

Conversation Memory:
{memory}

Retrieved Context:
{context}

Tool Result:
{tool_result}

Generate an accurate response.
"""


# =========================================================
# ANALYTICS TOOL
# =========================================================

class AnalyticsService:

    @staticmethod
    async def execute() -> ToolResult:

        async with AsyncSessionLocal() as db:

            stats = await get_system_stats(db)

            return ToolResult(
                success=True,
                data=stats
            )


# =========================================================
# DOCUMENT SEARCH TOOL
# =========================================================

class DocumentSearchService:

    @staticmethod
    async def execute(
        query: str,
        role: str,
        department: str
    ) -> ToolResult:

        async with AsyncSessionLocal() as db:

            docs = await search_documents_tool(
                db=db,
                query=query,
                user_role=role,
                user_department=department
            )

            return ToolResult(
                success=True,
                data={
                    "documents": docs
                }
            )


# =========================================================
# RETRIEVAL SERVICE
# =========================================================

class RetrievalService:

    @staticmethod
    async def retrieve(
        query: str,
        role: str,
        department: str
    ) -> RetrievalResult:

        async with AsyncSessionLocal() as db:

            result = await retrieve_context(
                db=db,
                query=query,
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


# =========================================================
# LANGUAGE SERVICE
# =========================================================

class LanguagePipeline:

    @staticmethod
    async def process_input(
        query: str
    ):

        language = detect_language(query)

        translated_query = query

        if language != "en":

            translated_query = translate_to_english(query)

        return translated_query, language

    @staticmethod
    async def process_output(
        response: str,
        language: str
    ):

        if language == "en":
            return response

        return translate_response(
            response,
            language
        )


# =========================================================
# GRAPH NODES
# =========================================================

async def classify_node(state: AgentState):

    intent = await IntentClassifierService.classify(
        state["query"]
    )

    return {
        **state,
        "intent": intent.value
    }


async def preprocessing_node(state: AgentState):

    query, language = await LanguagePipeline.process_input(
        state["query"]
    )

    memory_task = SemanticMemoryService.load_memory(
        state["session_id"]
    )

    rewrite_task = QueryRewriteService.rewrite(
        query
    )

    memory, rewritten = await asyncio.gather(
        memory_task,
        rewrite_task
    )

    return {
        **state,
        "query": query,
        "language": language,
        "memory_context": memory,
        "rewritten_query": rewritten
    }


async def planner_node(state: AgentState):

    if state["intent"] != IntentType.MULTISTEP.value:

        return {
            **state,
            "plan": ""
        }

    plan = await PlanningService.create_plan(
        state["query"]
    )

    return {
        **state,
        "plan": plan
    }


async def retrieval_node(state: AgentState):

    result = await RetrievalService.retrieve(
        query=state["rewritten_query"],
        role=state["user_role"],
        department=state["user_department"]
    )

    return {
        **state,
        "context": result.context,
        "sources": result.sources,
        "needs_general_knowledge":
            result.needs_general_knowledge,
        "response": result.message
    }


async def analytics_node(state: AgentState):

    result = await AnalyticsService.execute()

    return {
        **state,
        "tool_result": result.data
    }


async def search_node(state: AgentState):

    result = await DocumentSearchService.execute(
        query=state["rewritten_query"],
        role=state["user_role"],
        department=state["user_department"]
    )

    return {
        **state,
        "tool_result": result.data
    }


async def generation_node(state: AgentState):

    if state.get("needs_general_knowledge"):

        return state

    prompt = ContextBuilderService.build(
        memory=state["memory_context"],
        context=state["context"],
        tool_result=state["tool_result"],
        plan=state["plan"]
    )

    final_prompt = f"""
{prompt}

USER QUESTION:
{state["query"]}

ANSWER:
"""

    response = await llm_manager.generate_response(
        prompt=final_prompt,
        user_id=state["user_id"],
        temperature=0.3,
        stream=False
    )

    final_response = response["response"]

    final_response = await LanguagePipeline.process_output(
        final_response,
        state["language"]
    )

    await memory_service.save_memory(
        session_id=state["session_id"],
        role="user",
        message=state["query"]
    )

    await memory_service.save_memory(
        session_id=state["session_id"],
        role="assistant",
        message=final_response
    )

    return {
        **state,
        "response": final_response
    }


# =========================================================
# ROUTER
# =========================================================

def router(state: AgentState):

    intent = state["intent"]

    if intent == IntentType.ANALYTICS.value:
        return "analytics"

    if intent == IntentType.SEARCH.value:
        return "search"

    if intent == IntentType.RAG.value:
        return "retrieve"

    if intent == IntentType.MULTISTEP.value:
        return "retrieve"

    return "generate"


# =========================================================
# BUILD GRAPH
# =========================================================

graph = StateGraph(AgentState)

graph.add_node(
    "classify",
    classify_node
)

graph.add_node(
    "preprocess",
    preprocessing_node
)

graph.add_node(
    "planner",
    planner_node
)

graph.add_node(
    "retrieve",
    retrieval_node
)

graph.add_node(
    "analytics",
    analytics_node
)

graph.add_node(
    "search",
    search_node
)

graph.add_node(
    "generate",
    generation_node
)

graph.set_entry_point("classify")

graph.add_edge(
    "classify",
    "preprocess"
)

graph.add_edge(
    "preprocess",
    "planner"
)

graph.add_conditional_edges(
    "planner",
    router,
    {
        "analytics": "analytics",
        "search": "search",
        "retrieve": "retrieve",
        "generate": "generate"
    }
)

graph.add_edge(
    "analytics",
    "generate"
)

graph.add_edge(
    "search",
    "generate"
)

graph.add_edge(
    "retrieve",
    "generate"
)

graph.add_edge(
    "generate",
    END
)

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
        user_role: str,
        user_department: str
    ) -> AgentResponse:

        request_id = str(uuid.uuid4())

        started_at = time.time()

        logger.info(
            f"Agent execution started: {request_id}"
        )

        state: AgentState = {

            "query": query,

            "rewritten_query": "",

            "session_id": session_id,

            "user_id": user_id,

            "user_role": user_role,

            "user_department": user_department,

            "request_id": request_id,

            "intent": "",

            "language": "en",

            "memory_context": "",

            "plan": "",

            "context": "",

            "sources": [],

            "tool_result": {},

            "response": "",

            "needs_general_knowledge": False
        }

        result = await execute_with_retry(
            agent.ainvoke(state)
        )

        latency = int(
            (time.time() - started_at) * 1000
        )

        logger.info(
            f"Agent completed: {request_id} | {latency}ms"
        )

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
    user_role: str,
    user_department: str
):

    result = await AgentRuntime.execute(
        query=query,
        session_id=session_id,
        user_id=user_id,
        user_role=user_role,
        user_department=user_department
    )

    return result.response