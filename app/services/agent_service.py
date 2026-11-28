"""
Enterprise Agent Service Façade
================================
This module serves as the authoritative public entry point and backward-compatible façade
for the Patwatoli AI modular agent runtime architecture.

All domain logic, state management, LangGraph nodes, and services are decoupled into:
  - app.services.agent.schemas
  - app.services.agent.services.*
  - app.services.agent.nodes.*
  - app.services.agent.graph
"""

from __future__ import annotations

from app.services.agent.schemas import (
    AgentResponse,
    AgentState,
    ExecutionMetadata,
    IntentType,
    MAX_MEMORY_MESSAGES,
    REQUEST_TIMEOUT,
    RETRY_ATTEMPTS,
    RetrievalResult,
    ToolResult,
    execute_with_retry,
    logger,
)
from app.services.agent.services.classifier import IntentClassifierService
from app.services.agent.services.context_builder import (
    CONVERSATIONAL_MEMORY_DIRECTIVE,
    GENERAL_CHAT_MASTER_PROMPT,
    ContextBuilderService,
    is_conversational_memory_query,
)
from app.services.agent.services.memory import SemanticMemoryService
from app.services.agent.services.query_planner import (
    PlanningService,
    QueryRewriteService,
)
from app.services.agent.services.tools import (
    AnalyticsService,
    DocumentSearchService,
    LanguagePipeline,
    RetrievalService,
)
from app.services.agent.nodes import (
    analytics_node,
    assistant_runtime_node,
    cag_node,
    classify_node,
    finance_node,
    generation_node,
    image_gen_node,
    planner_node,
    preprocessing_node,
    retrieval_node,
    search_node,
)
from app.services.agent.graph import (
    AgentRuntime,
    agent,
    graph,
    router,
    run_agent,
)

__all__ = [
    # Core Public Interface
    "run_agent",
    "AgentRuntime",
    "agent",
    "graph",
    "router",
    # Types & Schemas
    "AgentState",
    "IntentType",
    "RetrievalResult",
    "ToolResult",
    "ExecutionMetadata",
    "AgentResponse",
    "execute_with_retry",
    "MAX_MEMORY_MESSAGES",
    "REQUEST_TIMEOUT",
    "RETRY_ATTEMPTS",
    "logger",
    # Services
    "IntentClassifierService",
    "SemanticMemoryService",
    "QueryRewriteService",
    "PlanningService",
    "ContextBuilderService",
    "GENERAL_CHAT_MASTER_PROMPT",
    "CONVERSATIONAL_MEMORY_DIRECTIVE",
    "is_conversational_memory_query",
    "AnalyticsService",
    "DocumentSearchService",
    "RetrievalService",
    "LanguagePipeline",
    # Graph Nodes
    "assistant_runtime_node",
    "cag_node",
    "classify_node",
    "preprocessing_node",
    "planner_node",
    "retrieval_node",
    "analytics_node",
    "search_node",
    "finance_node",
    "generation_node",
    "image_gen_node",
]
