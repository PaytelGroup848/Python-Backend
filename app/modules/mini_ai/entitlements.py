from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.usage.services.usage_limit_service import usage_limit_service

FREE_MAX_BOTS = 1
FREE_MAX_CHUNKS = 50
PAID_MAX_BOTS = 5
PAID_MAX_CHUNKS = 200
PAID_MONTHLY_PUBLIC_MESSAGES = 5000


class MiniAIEntitlements(BaseModel):
    plan_tier: str  # "free" | "paid"
    plan_name: str
    max_bots: int
    max_chunks_per_bot: int
    allow_public_embed: bool
    allow_insights: bool
    monthly_public_messages_limit: int


async def get_mini_ai_entitlements(
    db: AsyncSession,
    user_id: int,
) -> MiniAIEntitlements:
    raw_plan = await usage_limit_service.get_user_plan(db, user_id)
    plan_name = str(raw_plan or "free").strip()
    is_paid = plan_name.lower() not in {"", "free"}

    if is_paid:
        return MiniAIEntitlements(
            plan_tier="paid",
            plan_name=plan_name,
            max_bots=PAID_MAX_BOTS,
            max_chunks_per_bot=PAID_MAX_CHUNKS,
            allow_public_embed=True,
            allow_insights=True,
            monthly_public_messages_limit=PAID_MONTHLY_PUBLIC_MESSAGES,
        )

    return MiniAIEntitlements(
        plan_tier="free",
        plan_name="Free",
        max_bots=FREE_MAX_BOTS,
        max_chunks_per_bot=FREE_MAX_CHUNKS,
        allow_public_embed=False,
        allow_insights=False,
        monthly_public_messages_limit=0,
    )
