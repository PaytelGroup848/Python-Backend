from __future__ import annotations

import logging

from app.services.agent.schemas import AgentState

logger = logging.getLogger("enterprise_agent")


async def finance_node(state: AgentState):
    query = (state.get("rewritten_query") or "").strip() or state["query"]

    from app.modules.finance.finance_service import finance_service
    market_context = None
    try:
        market_context = await finance_service.get_market_context(query)
    except Exception as exc:
        logger.warning(f"Market context retrieval error in finance_node: {exc}")

    current_context = state.get("context", "")
    if market_context:
        combined_context = f"{current_context}\n\n{market_context}".strip() if current_context else market_context
    else:
        combined_context = current_context

    return {
        **state,
        "context": combined_context,
        "tool_result": {"finance_data": market_context} if market_context else {}
    }
