from __future__ import annotations

import asyncio
import logging
import os
import re
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END

from app.db.database import AsyncSessionLocal

from app.modules.provider_runtime.manager.provider_runtime_manager import (
    provider_runtime_manager,
)

from app.modules.retrieval_runtime.services.rag_service import (
    retrieve_context
)

from app.modules.assistants.services.assistant_runtime_service import (
    assistant_runtime_service
)

from app.modules.memory.services.memory_service import (
    memory_service
)

from app.modules.memory.services.cag_service import (
    cag_service
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

from app.modules.usage.services.usage_limit_service import (
    usage_limit_service
)

# =========================================================
# LOGGING
# =========================================================

logger = logging.getLogger("enterprise_agent")

# =========================================================
# CONFIG
# =========================================================

MAX_MEMORY_MESSAGES = 6
REQUEST_TIMEOUT = 120
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
    IMAGE_GEN = "image_gen"
    IMAGE_EDIT = "image_edit"


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
    assistant_id: int | None
    user_role: str
    user_department: str

    # runtime
    request_id: str
    intent: str
    language: str

    system_prompt: str
    assistant_name: str
    assistant_code: str

    model_id: int | None

    temperature: float
    top_p: float

    max_tokens: int
    context_window: int

    memory_enabled: bool
    rag_enabled: bool
    cag_enabled: bool
    tool_calling_enabled: bool

    # CAG
    cag_hit: bool
    cag_response: str

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
    aspect_ratio: Optional[str]
    web_sources: Optional[list]
    web_search: Optional[bool]
    stream_handler: Optional[Any]

    # metadata
    needs_general_knowledge: bool


# =========================================================
# RETRY + TIMEOUT WRAPPER
# =========================================================

async def execute_with_retry(

    func,

    *args,

    retries: int = RETRY_ATTEMPTS,

    timeout: int = REQUEST_TIMEOUT
):

    last_error = None

    for attempt in range(retries):

        try:

            return await asyncio.wait_for(
                func(*args),
                timeout=timeout
            )

        except Exception as e:

            last_error = e

            logger.exception(
                f"Retry attempt failed: {attempt + 1}"
            )

            await asyncio.sleep(1)

    if last_error is not None:
        raise last_error
    
    raise RuntimeError("execute_with_retry failed: no attempts were made")


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

        # Image generation intent detection (typo-tolerant, flexible phrasing, Hindi/Hinglish)
        negative_image_phrases = [
            "draw a conclusion", "draw conclusions",
            "draw comparison", "draw comparisons",
            "draw inspiration", "draw from"
        ]
        if not any(neg in q for neg in negative_image_phrases):
            # Pattern 1: Action verb (with typo tolerance e.g. genrate) + words + visual noun
            # Matches: "genrate the image of cat", "generate an image of...", "create a picture of...", "make photo of..."
            image_verb_noun_regex = r"\b(gen[e]?r[a]?te|creat[e]?|make|draw|paint|render|produce|show\s+me|give\s+me)\b.{0,30}\b(image|images|picture|pictures|photo|photos|pic|pics|artwork|illustration|portrait|wallpaper|tasveer)\b"

            # Pattern 2: Visual noun + preposition ("image of a cat", "picture for my banner", "photo showing ...")
            image_direct_noun_regex = r"\b(image|images|picture|pictures|photo|photos|pic|pics|artwork|illustration|tasveer)\s+(of|for|showing|depicting)\b"

            # Pattern 3: Direct creative action ("draw a cat", "paint an astronaut", "sketch me a lion")
            image_direct_draw_regex = r"\b(draw|paint|sketch|illustrate)\s+(a|an|the|me\s+a|me\s+an)\b"

            # Pattern 4: Common Hindi/Hinglish phrasing
            hinglish_image_terms = [
                "tasveer banao", "photo banao", "image banao", "pic banao",
                "tasveer bana", "photo bana", "image bana", "pic bana",
                "tasveer banaye", "photo banaye", "image banaye",
                "tasveer chahiye", "photo chahiye", "image chahiye"
            ]

            if (
                re.search(image_verb_noun_regex, q)
                or re.search(image_direct_noun_regex, q)
                or re.search(image_direct_draw_regex, q)
                or any(t in q for t in hinglish_image_terms)
                or "--ar " in q
                or q.startswith("/imagine")
            ):
                return IntentType.IMAGE_GEN

            # Conversational Image Edit intent detection
            edit_patterns = [
                r"\b(edit|modify|tweak|alter|remix)\b.{0,25}\b(image|picture|photo|pic|artwork|tasveer)\b",
                r"\b(change|turn|make|replace)\b.{0,30}\b(color|colour|background|bg|outfit|hair|lighting|style|sky|car|clothes|shirt)\b",
                r"\b(add|put|insert)\b.{0,30}\b(to\s+(the\s+)?(image|picture|photo|pic|scene)|in\s+(the\s+)?(image|picture|photo|pic|scene))\b",
                r"\b(remove|delete|erase)\b.{0,30}\b(from\s+(the\s+)?(image|picture|photo|pic|scene)|background|bg)\b",
                r"\b(upscale|4k|super\s+resolution)\b",
            ]
            hinglish_edit_terms = [
                "color change", "colour change", "background change", "bg change",
                "image edit", "photo edit", "pic edit", "tasveer edit",
                "isme change karo", "isme add karo", "isme se hatao", "bg hatao", "background hatao",
                "4k banao", "upscale karo", "clear karo image"
            ]
            if (
                any(re.search(p, q) for p in edit_patterns)
                or any(t in q for t in hinglish_edit_terms)
            ):
                return IntentType.IMAGE_EDIT

        if any(x in q for x in analytics_terms):
            return IntentType.ANALYTICS

        # Web Search / Real-time live info detection
        web_search_terms = [
            "search the web", "search online", "search internet", "browse the web", "google", "web search",
            "latest news", "current news", "recent news", "today's news",
            "latest updates", "recent developments", "current price", "today's price",
            "who won the", "match score", "current weather", "who is the current"
        ]
        web_search_patterns = [
            r"\b(search\s+(the\s+)?web|search\s+online|search\s+internet|google\s+this|browse\s+the\s+web)\b",
            r"\b(latest|current|recent|today's|today|yesterday|upcoming)\b.{0,30}\b(news|update|updates|version|release|price|score|weather|event|events|election|status)\b",
            r"\b(who\s+is\s+the\s+current|what\s+is\s+the\s+latest|what\s+is\s+the\s+current)\b",
            r"^(\/search|search:|\?)\s*",
            r"\[web search\]",
            r"--search",
        ]
        if (
            any(t in q for t in web_search_terms)
            or any(re.search(p, q) for p in web_search_patterns)
        ):
            return IntentType.SEARCH

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
    async def rewrite(
        query: str,
        user_id: int
    ) -> str:

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
            # Clean unwanted preamble or markdown
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



# =========================================================
# PLANNER SERVICE
# =========================================================

class PlanningService:

    @staticmethod
    async def create_plan(
        query: str,
        user_id: int
    ) -> str:

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
        system_prompt: str,
        memory: str,
        context: str,
        tool_result: dict,
        plan: str
    ) -> str:

        context = ContextBuilderService.sanitize_context(
            context
        )

        brand_directive = (
            "CORE PLATFORM DIRECTIVE (MANDATORY & TOP PRIORITY):\n"
            "You are Patwatoli AI, a premier enterprise AI platform created, developed, and owned by Patwatoli.\n"
            "Regardless of your specific role or assistant persona (e.g. General Chat, Code Architect, LawGPT, MedAssist AI, Astrology AI, etc.):\n"
            "1. If asked who you are, who created you, who trained you, or 'apne bare mein batao', you MUST ALWAYS state that you are Patwatoli AI (or the specialized assistant of Patwatoli AI), built and powered by Patwatoli.\n"
            "2. NEVER state, disclose, or imply that you are Mistral, OpenAI, Meta Llama, Google Gemini, Anthropic, or any third-party foundation model provider.\n"
            "3. Always maintain the highest standard of accuracy, professionalism, and helpfulness."
        )

        active_role_prompt = (
            system_prompt.strip()
            if system_prompt and system_prompt.strip()
            else "You are General Chat, a helpful, versatile universal AI assistant within Patwatoli AI."
        )

        return f"""
            {brand_directive}

            Assistant Role & Instructions:
            {active_role_prompt}

            Execution Plan:
            {plan}

            Conversation Memory:
            {memory}

            Retrieved Context:
            {context}

            Tool Result:
            {tool_result}
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
                    data={
                        "documents": docs
                    }
                )
        except Exception as e:
            logger.warning(f"Document search execution failed: {e}")
            return ToolResult(
                success=True,
                data={
                    "documents": []
                }
            )


# =========================================================
# RETRIEVAL SERVICE
# =========================================================

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
async def assistant_runtime_node(
        state: AgentState
    ):

        if state["assistant_id"] is None:

            return {

                **state,

                "system_prompt": "",

                "assistant_name": "General Chat",

                "assistant_code": "GENERAL",

                "model_id": None,

                "temperature": 0.2,

                "top_p": 0.95,

                "max_tokens": 4000,

                "context_window": 8000,

                "memory_enabled": True,

                "rag_enabled": False,

                "cag_enabled": False,

                "tool_calling_enabled": False,
            }

        async with AsyncSessionLocal() as db:

            runtime = await (
                assistant_runtime_service
                .load_runtime(
                    db=db,
                    assistant_id=state["assistant_id"]
                )
            )

        return {

    **state,

        "system_prompt":
            runtime.system_prompt or "",

        "assistant_name":
            runtime.assistant_name,

        "assistant_code":
            runtime.assistant_code,

        "model_id":
            runtime.model_id,

        "temperature":
            runtime.temperature,

        "top_p":
            runtime.top_p,

        "max_tokens":
            runtime.max_tokens,

        "context_window":
            runtime.context_window,

        "memory_enabled":
            runtime.memory_enabled,

        "rag_enabled":
            runtime.rag_enabled,

        "cag_enabled":
            runtime.cag_enabled,

        "tool_calling_enabled":
            runtime.tool_calling_enabled
    }

async def cag_node(
    state: AgentState
):

    if not state["cag_enabled"]:

        return state

    cached = await (
        cag_service.get_response(
            assistant_id=
                state["assistant_id"],

            query=
                state["query"]
        )
    )

    if not cached:

        logger.info(
            f"CAG MISS: {state['query']}"
        )

        return state
    logger.info(
        f"CAG HIT: {state['query']}"
    )

    return {

        **state,

        "cag_hit": True,

        "cag_response":
            cached["response"],

        "response":
            cached["response"]
    }

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


    if state["memory_enabled"]:

        memory_task = (
            SemanticMemoryService
            .load_memory(
                state["session_id"]
            )
        )

    else:

        memory_task = asyncio.sleep(
            0,
            result=""
        )

    is_web_search = bool(state.get("web_search", False))
    clean_query = query
    q_lower = query.lower()
    if "[web search]" in q_lower or q_lower.startswith("/search") or "--search" in q_lower:
        is_web_search = True
        clean_query = re.sub(r"\[web search\]", "", clean_query, flags=re.IGNORECASE)
        clean_query = re.sub(r"^\/search\s*", "", clean_query, flags=re.IGNORECASE)
        clean_query = re.sub(r"--search", "", clean_query, flags=re.IGNORECASE).strip()

    rewrite_task = QueryRewriteService.rewrite(
        query=clean_query,
        user_id=state["user_id"]
    )

    memory, rewritten = await asyncio.gather(
        memory_task,
        rewrite_task
    )

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


async def retrieval_node(state: AgentState):

    res_context = ""
    res_sources = []
    res_needs_gk = False
    res_msg = ""

    if state.get("rag_enabled"):
        query_to_use = (state.get("rewritten_query") or "").strip() or state["query"]
        result = await RetrievalService.retrieve(
            query=query_to_use,
            assistant_id=state["assistant_id"],
            role=state["user_role"],
            department=state["user_department"]
        )

        res_context = result.get("context", "") if isinstance(result, dict) else getattr(result, "context", "")

        if not res_context and state["query"] != query_to_use:
            logger.info("Rewritten query returned no results. Retrying retrieval with raw user query.")
            result = await RetrievalService.retrieve(
                query=state["query"],
                assistant_id=state["assistant_id"],
                role=state["user_role"],
                department=state["user_department"]
            )
            res_context = result.get("context", "") if isinstance(result, dict) else getattr(result, "context", "")

        res_sources = list(result.get("sources", [])) if isinstance(result, dict) else list(getattr(result, "sources", []))
        res_needs_gk = result.get("needs_general_knowledge", False) if isinstance(result, dict) else getattr(result, "needs_general_knowledge", False)
        res_msg = result.get("message", "") if isinstance(result, dict) else getattr(result, "message", "")

    # Check if there is an uploaded document for this conversation or user
    doc_context = ""
    try:
        from sqlalchemy import select
        from app.shared.redis.client import redis_client
        from app.models.knowledge_base_document import KnowledgeBaseDocument
        from app.services.document_parser_service import parse_document
        import json

        session_id = str(state.get("session_id", "") or "")
        user_id = state.get("user_id")

        filename = None
        if session_id:
            raw_conv = await redis_client.get(f"conversation_pdf:{session_id}")
            if raw_conv:
                try:
                    conv_docs = json.loads(raw_conv)
                    if isinstance(conv_docs, list) and conv_docs:
                        filename = str(conv_docs[0])
                    elif isinstance(conv_docs, str):
                        filename = conv_docs
                except Exception:
                    filename = raw_conv

        if not filename and user_id:
            filename = await redis_client.get(f"latest_pdf:{user_id}")

        if filename:
            async with AsyncSessionLocal() as db:
                kb_res = await db.execute(
                    select(KnowledgeBaseDocument)
                    .filter(KnowledgeBaseDocument.file_name == filename)
                    .order_by(KnowledgeBaseDocument.id.desc())
                    .limit(1)
                )
                kb_doc = kb_res.scalar_one_or_none()

            if kb_doc and kb_doc.file_path:
                ext = os.path.splitext(kb_doc.file_path)[1].lower()
                if ext in [".png", ".jpg", ".jpeg", ".webp"]:
                    try:
                        from app.services.vision_service import VisionService
                        logger.info(f"Analyzing attached image with Multimodal Vision (Pixtral): {kb_doc.file_path}")
                        vision_analysis = await VisionService.analyze_image(
                            file_path=kb_doc.file_path,
                            prompt=state.get("query")
                        )
                        if vision_analysis:
                            doc_context = (
                                f"=== USER ATTACHED IMAGE ANALYSIS ({filename}) ===\n"
                                f"Visual Understanding & Inspection Details:\n{vision_analysis}\n"
                                f"=== END OF IMAGE ANALYSIS ==="
                            )
                        else:
                            doc_context = f"=== USER ATTACHED IMAGE ({filename}) ===\n[Image attached]\n=== END ==="
                        if not any((isinstance(s, dict) and s.get("source_file") == filename) for s in res_sources):
                            res_sources.append({"source_file": filename, "page_number": 1})
                    except Exception as ve:
                        logger.warning(f"Error analyzing attached image with vision service: {ve}")
                else:
                    pages = await parse_document(kb_doc.file_path)
                    if pages:
                        text_parts = []
                        for i, p in enumerate(pages[:50]):
                            txt = (p.get("text") or "").strip()
                            if txt:
                                text_parts.append(f"[Page {p.get('page_number', i+1)}]\n{txt}")

                        full_doc_text = "\n\n".join(text_parts)
                        if len(full_doc_text) > 12000:
                            full_doc_text = full_doc_text[:12000] + "\n\n[... Remaining pages omitted for length ...]"

                        if full_doc_text:
                            doc_context = f"=== USER ATTACHED DOCUMENT ({filename}) ===\n{full_doc_text}\n=== END OF ATTACHED DOCUMENT ==="
                            if not any((isinstance(s, dict) and s.get("source_file") == filename) for s in res_sources):
                                res_sources.append({"source_file": filename, "page_number": 1})
    except Exception as doc_err:
        logger.warning(f"Error loading attached document context: {doc_err}")

    if doc_context:
        if res_context:
            res_context = f"{doc_context}\n\n{res_context}"
        else:
            res_context = doc_context

    # Live Web Search fallback or explicit web search in retrieval_node
    web_sources = list(state.get("web_sources") or [])
    if state.get("web_search") or (res_needs_gk and state.get("query")):
        try:
            from app.services.web_search_service import web_search_service
            query_to_search = (state.get("rewritten_query") or "").strip() or state["query"]
            web_results = await asyncio.to_thread(web_search_service.search, query_to_search, max_results=5)
            if web_results:
                web_ctx = web_search_service.format_search_context(web_results)
                if res_context:
                    res_context = f"{res_context}\n\n{web_ctx}"
                else:
                    res_context = web_ctx
                web_sources = [{"title": r["title"], "url": r["url"]} for r in web_results]
                res_needs_gk = False
        except Exception as ws_err:
            logger.warning(f"Web search in retrieval_node failed: {ws_err}")

    return {
        **state,
        "context": res_context,
        "sources": res_sources,
        "web_sources": web_sources,
        "needs_general_knowledge": res_needs_gk,
        "response": res_msg
    }


async def analytics_node(state: AgentState):

    result = await AnalyticsService.execute()

    return {
        **state,
        "tool_result": result.data
    }


async def search_node(state: AgentState):

    query = (state.get("rewritten_query") or "").strip() or state["query"]

    # 1. Internal Document Search
    result = await DocumentSearchService.execute(
        query=query,
        role=state["user_role"],
        department=state["user_department"]
    )

    # 2. Live Web Search
    from app.services.web_search_service import web_search_service
    web_results = []
    try:
        web_results = await asyncio.to_thread(web_search_service.search, query, max_results=5)
    except Exception as exc:
        logger.warning(f"Web search in search_node error: {exc}")

    web_context = web_search_service.format_search_context(web_results) if web_results else ""
    web_sources = [
        {"title": r["title"], "url": r["url"]}
        for r in web_results
    ]

    current_context = state.get("context", "")
    if web_context:
        combined_context = f"{current_context}\n\n{web_context}".strip() if current_context else web_context
    else:
        combined_context = current_context

    tool_data = dict(result.data) if hasattr(result, "data") else {}
    if web_results:
        tool_data["web_search"] = web_results

    return {
        **state,
        "context": combined_context,
        "tool_result": tool_data,
        "web_sources": web_sources
    }


async def generation_node(state: AgentState):

    if state.get("cag_hit"):
        return state

    asst_code = str(state.get("assistant_code") or "").lower()
    allow_external_fallback = asst_code in ["general", "coder"] or "code" in asst_code or "general" in asst_code

    if state.get("needs_general_knowledge") and not allow_external_fallback:
        return state

    prompt = ContextBuilderService.build(
        system_prompt=state.get("system_prompt", ""),
        memory=state.get("memory_context", ""),
        context=state.get("context", ""),
        tool_result=state.get("tool_result", {}),
        plan=state.get("plan", "")
    )

    web_sources = state.get("web_sources", [])
    web_citation_instr = ""
    if web_sources or "REAL-TIME LIVE WEB SEARCH RESULTS" in state.get("context", ""):
        web_citation_instr = "\nINSTRUCTION: You have real-time live web search results above. Use them to provide an accurate, up-to-date answer. Cite your factual statements with inline citation numbers like [1], [2] corresponding to the search results above.\n"

    final_prompt = f"""
    {prompt}
    {web_citation_instr}
    USER QUESTION:
    {state["query"]}

    ANSWER:
    """

    async with AsyncSessionLocal() as db:
        allowed = await usage_limit_service.check_usage_limit(
            db,
            user_id=state["user_id"],
        )

        if not allowed:
            raise Exception("Plan limit exceeded")

        stream_handler = state.get("stream_handler")
        collected_chunks = []
        if stream_handler and callable(stream_handler):
            try:
                async for chunk in provider_runtime_manager.stream_response(final_prompt):
                    if chunk:
                        collected_chunks.append(chunk)
                        try:
                            await stream_handler({"type": "chunk", "content": chunk})
                        except Exception as cb_err:
                            logger.warning(f"Stream callback error: {cb_err}")
                final_response = "".join(collected_chunks)
            except Exception as exc:
                logger.warning(f"Streaming provider error, falling back to batch: {exc}")
                if state.get("context"):
                    final_response = f"Based on retrieved context:\n\n{state['context']}"
                else:
                    response = await provider_runtime_manager.generate_response(
                        prompt=final_prompt,
                        user_id=state["user_id"],
                        temperature=state.get("temperature", 0.3),
                        stream=False
                    )
                    final_response = response["response"]
                if not collected_chunks:
                    try:
                        await stream_handler({"type": "chunk", "content": final_response})
                    except Exception:
                        pass
        else:
            try:
                response = await provider_runtime_manager.generate_response(
                    prompt=final_prompt,
                    user_id=state["user_id"],
                    temperature=state.get("temperature", 0.3),
                    stream=False
                )
                final_response = response["response"]
            except Exception as exc:
                if state.get("context"):
                    logger.info("External provider unavailable, returning dataset context directly.")
                    final_response = f"Based on retrieved context:\n\n{state['context']}"
                else:
                    raise exc

    # Cleanly append web sources (Perplexity style)
    if web_sources and isinstance(web_sources, list):
        web_links = []
        for i, ws in enumerate(web_sources, start=1):
            title = ws.get("title") or f"Source {i}"
            url = ws.get("url") or "#"
            web_links.append(f"[{i}] [{title}]({url})")
        if web_links and "**🌐 Sources:**" not in final_response:
            web_suffix = "\n\n**🌐 Sources:**\n" + "\n".join(web_links)
            final_response += web_suffix
            if stream_handler and callable(stream_handler):
                try:
                    await stream_handler({"type": "chunk", "content": web_suffix})
                except Exception:
                    pass

    # Cleanly append internal document citations if sources were retrieved with context
    sources_list = state.get("sources", [])
    if sources_list and isinstance(sources_list, list) and state.get("context"):
        source_pills = []
        seen_sources = set()
        for s in sources_list:
            if isinstance(s, dict):
                f_name = s.get("source_file", "Document")
                p_num = s.get("page_number")
                page_str = f" (Page {p_num})" if p_num else ""
                pill = f"`📄 {f_name}{page_str}`"
            else:
                pill = f"`📄 {s}`"
            if pill not in seen_sources:
                seen_sources.add(pill)
                source_pills.append(pill)
        if source_pills and source_pills[0] not in final_response:
            doc_suffix = "\n\n**📌 Documents:**\n" + "  ".join(source_pills)
            final_response += doc_suffix
            if stream_handler and callable(stream_handler):
                try:
                    await stream_handler({"type": "chunk", "content": doc_suffix})
                except Exception:
                    pass

    if state.get("cag_enabled"):
        await (
            cag_service.save_response(
                assistant_id=state["assistant_id"],
                query=state["query"],
                response=final_response
            )
        )
        logger.info(f"CAG SAVE: {state['query']}")

    final_response = await LanguagePipeline.process_output(
        final_response,
        state["language"]
    )

    if state.get("memory_enabled"):
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


async def image_gen_node(state: AgentState):
    from app.services.image_generation_service import image_generation_service
    from app.services.image_providers.base import ContentPolicyViolationError

    user_id = state.get("user_id") or 1
    session_id_raw = state.get("session_id")
    conv_id = int(session_id_raw) if session_id_raw and str(session_id_raw).isdigit() else None
    query = state.get("query", "")

    # Aspect ratio detection: supports explicit state param or Midjourney-style flags (--ar 16:9, --ar 9:16, 16:9, landscape, portrait)
    aspect_ratio_param = state.get("aspect_ratio") or "1024x1024"
    clean_prompt = query
    q_lower = query.lower()
    if "--ar 16:9" in q_lower or "16:9" in q_lower or "landscape" in q_lower or "widescreen" in q_lower:
        aspect_ratio_param = "1280x720"
        clean_prompt = re.sub(r"--ar\s+16:9", "", clean_prompt, flags=re.IGNORECASE).strip()
    elif "--ar 9:16" in q_lower or "9:16" in q_lower or "portrait" in q_lower or "vertical" in q_lower:
        aspect_ratio_param = "720x1280"
        clean_prompt = re.sub(r"--ar\s+9:16", "", clean_prompt, flags=re.IGNORECASE).strip()
    elif "--ar 1:1" in q_lower or "1:1" in q_lower or "square" in q_lower:
        aspect_ratio_param = "1024x1024"
        clean_prompt = re.sub(r"--ar\s+1:1", "", clean_prompt, flags=re.IGNORECASE).strip()
    elif aspect_ratio_param in ["16:9", "1280x720"]:
        aspect_ratio_param = "1280x720"
    elif aspect_ratio_param in ["9:16", "720x1280"]:
        aspect_ratio_param = "720x1280"
    else:
        aspect_ratio_param = "1024x1024"

    # Look for most recent generated image in this conversation session
    parent_image = None
    try:
        from app.models.generated_image import GeneratedImage
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            if conv_id:
                p_res = await db.execute(
                    select(GeneratedImage)
                    .filter(GeneratedImage.conversation_id == conv_id, GeneratedImage.status == "completed")
                    .order_by(GeneratedImage.id.desc())
                    .limit(1)
                )
                parent_image = p_res.scalar_one_or_none()
            if not parent_image and user_id:
                p_res = await db.execute(
                    select(GeneratedImage)
                    .filter(GeneratedImage.user_id == user_id, GeneratedImage.status == "completed")
                    .order_by(GeneratedImage.id.desc())
                    .limit(1)
                )
                parent_image = p_res.scalar_one_or_none()
    except Exception as db_err:
        logger.warning(f"Parent image lookup error: {db_err}")

    # Special Direct Chat Command: 1-Click Background Removal
    if parent_image and any(bg in q_lower for bg in ["remove background", "remove bg", "transparent background", "background remove", "bg hatao"]):
        try:
            bg_result = await image_generation_service.remove_background(
                user_id=user_id,
                image_id=parent_image.id,
            )
            bg_url = bg_result["file_url"]
            response_md = f"![Transparent Cutout]({bg_url})\n\n**1-Click Background Removed:** Transparent PNG cutout ready for download or presentation."
            return {
                **state,
                "response": response_md,
                "metadata": {**state.get("metadata", {}), "image_url": bg_url, "edit_type": "remove_bg"}
            }
        except Exception as bg_err:
            logger.error(f"Chat background removal failed: {bg_err}")

    # Special Direct Chat Command: 4K Upscaling
    if parent_image and any(up in q_lower for up in ["upscale", "4k", "super resolution", "enhance resolution"]):
        try:
            up_result = await image_generation_service.upscale_image(
                user_id=user_id,
                image_id=parent_image.id,
                scale=4,
            )
            up_url = up_result["file_url"]
            dims = up_result.get("dimensions", "4096x4096")
            response_md = f"![4K Ultra HD]({up_url})\n\n**AI 4K Super-Resolution Enhanced ({dims}):** 4x ultra-crisp resolution ready for download."
            return {
                **state,
                "response": response_md,
                "metadata": {**state.get("metadata", {}), "image_url": up_url, "edit_type": "upscale_4k"}
            }
        except Exception as up_err:
            logger.error(f"Chat upscale failed: {up_err}")

    # Conversational Image Editing
    is_edit = False
    parent_id = None
    target_prompt = clean_prompt or query
    intent = state.get("intent")
    if parent_image and (
        intent == IntentType.IMAGE_EDIT.value
        or any(w in q_lower for w in ["change", "make the", "turn the", "add ", "remove ", "replace ", "edit ", "modify ", "isme "])
    ):
        logger.info(f"Conversational image edit detected! Parent #{parent_image.id}: '{parent_image.original_prompt}'")
        target_prompt = await image_generation_service.synthesize_edit_prompt(
            original_prompt=parent_image.original_prompt,
            edit_instruction=clean_prompt or query,
            user_id=user_id
        )
        parent_id = parent_image.id
        is_edit = True
        if aspect_ratio_param == "1024x1024" and parent_image.aspect_ratio:
            aspect_ratio_param = parent_image.aspect_ratio

    stream_handler = state.get("stream_handler")
    if stream_handler and callable(stream_handler):
        try:
            await stream_handler({"type": "stage", "stage": "generating", "message": "Synthesizing artwork..."})
        except Exception:
            pass

    try:
        result = await image_generation_service.generate_and_persist(
            user_id=user_id,
            conversation_id=conv_id,
            prompt=target_prompt,
            aspect_ratio=aspect_ratio_param,
            parent_image_id=parent_id,
            edit_type="edit" if is_edit else "generation",
        )
        file_url = result["file_url"]
        ar_display = "16:9 Widescreen" if aspect_ratio_param == "1280x720" else ("9:16 Portrait" if aspect_ratio_param == "720x1280" else "1:1 Square")
        if is_edit and parent_image:
            response_md = f"![{target_prompt}]({file_url})\n\n**Edited Artwork (v2):** *\"{target_prompt}\"* ({ar_display})\n*✨ Modified from: \"{parent_image.original_prompt}\"*"
        else:
            response_md = f"![{clean_prompt or query}]({file_url})\n\n**Generated Artwork:** *\"{clean_prompt or query}\"* ({ar_display})"

        if stream_handler and callable(stream_handler):
            try:
                await stream_handler({"type": "stage", "stage": "completed", "message": "Artwork generated"})
            except Exception:
                pass

        if state.get("memory_enabled") and state.get("session_id"):
            try:
                await memory_service.save_memory(
                    session_id=state["session_id"],
                    role="user",
                    message=state["query"]
                )
                await memory_service.save_memory(
                    session_id=state["session_id"],
                    role="assistant",
                    message=response_md
                )
            except Exception as mem_err:
                logger.warning(f"Failed to save image memory: {mem_err}")

        return {
            **state,
            "response": response_md,
            "metadata": {
                **state.get("metadata", {}),
                "image_url": file_url,
                "provider": result.get("provider"),
                "model_name": result.get("model_name"),
            }
        }
    except ContentPolicyViolationError as cpv:
        return {
            **state,
            "response": f"⚠️ **Content Policy Violation**: {str(cpv)}\nYour prompt could not be processed, and no credits were deducted."
        }
    except Exception as exc:
        logger.error(f"Image generation node failure: {exc}")
        return {
            **state,
            "response": f"⚠️ **Image Generation Failed**: {str(exc)}\nPlease try again. Any reserved credits have been restored."
        }


# =========================================================
# ROUTER
# =========================================================

def router(state: AgentState):

    intent = state["intent"]

    if intent in (IntentType.IMAGE_GEN.value, IntentType.IMAGE_EDIT.value):
        return "image_gen"

    if intent == IntentType.ANALYTICS.value:
        return "analytics"

    if intent == IntentType.SEARCH.value or state.get("web_search"):
        return "search"

    return "retrieve"


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
    "assistant_runtime",
    assistant_runtime_node
)
graph.add_node(
    "cag",
    cag_node
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

graph.add_node(
    "image_gen",
    image_gen_node
)

graph.set_entry_point("classify")

graph.add_edge(
    "classify",
    "preprocess"
)

graph.add_edge(
    "preprocess",
    "assistant_runtime"
)

graph.add_edge(
    "assistant_runtime",
    "cag"
)

graph.add_edge(
    "cag",
    "planner"
)

graph.add_conditional_edges(
    "planner",
    router,
    {
        "analytics": "analytics",
        "search": "search",
        "retrieve": "retrieve",
        "generate": "generate",
        "image_gen": "image_gen",
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

graph.add_edge(
    "image_gen",
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
        assistant_id: int | None,
        user_role: str,
        user_department: str,
        aspect_ratio: str = "1024x1024",
        web_search: bool = False,
        stream_handler: Optional[Any] = None
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

            "rag_enabled": True,

            "cag_enabled": False,

            "tool_calling_enabled": False,

            "cag_hit": False,

            "cag_response": "",

            "memory_context": "",

            "plan": "",

            "context": "",

            "sources": [],

            "web_sources": [],

            "web_search": web_search,

            "tool_result": {},

            "response": "",

            "aspect_ratio": aspect_ratio,

            "needs_general_knowledge": False,

            "stream_handler": stream_handler
        }

        result = await execute_with_retry(
            agent.ainvoke,
            state
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
    assistant_id: int | None,
    user_role: str,
    user_department: str,
    aspect_ratio: str = "1024x1024",
    web_search: bool = False,
    stream_handler: Optional[Any] = None
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
        stream_handler=stream_handler
    )

    return result.response