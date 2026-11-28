from __future__ import annotations

from app.services.agent.schemas import AgentState
from app.services.agent.services.tools import AnalyticsService


async def analytics_node(state: AgentState):
    result = await AnalyticsService.execute()
    return {
        **state,
        "tool_result": result.data
    }
