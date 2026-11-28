from __future__ import annotations

import asyncio
import logging
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, TypedDict

StreamHandler = Callable[[Dict[str, Any]], Awaitable[None]]

from pydantic import BaseModel, Field

logger = logging.getLogger("enterprise_agent")

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
    FINANCE = "finance"


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
    web_images: Optional[list]
    web_search: Optional[bool]
    stream_handler: Optional[StreamHandler]
    attached_docs: Optional[list]

    # metadata
    needs_general_knowledge: bool
    is_custom: Optional[bool]
    strict_rag: Optional[bool]


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
