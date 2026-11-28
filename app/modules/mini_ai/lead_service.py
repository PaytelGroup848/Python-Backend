from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.mini_ai.models import MiniAILead


async def capture_lead(
    db: AsyncSession,
    assistant_id: int,
    owner_user_id: int,
    visitor_name: str,
    visitor_contact: str,
    first_question: str | None = None,
) -> MiniAILead:
    lead = MiniAILead(
        assistant_id=assistant_id,
        owner_user_id=owner_user_id,
        visitor_name=visitor_name.strip()[:120],
        visitor_contact=visitor_contact.strip()[:160],
        first_question=(first_question or "").strip()[:1000] or None,
    )
    db.add(lead)
    await db.flush()
    await db.refresh(lead)
    return lead


async def list_leads(
    db: AsyncSession,
    assistant_id: int,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[MiniAILead], int]:
    total_res = await db.execute(
        select(func.count(MiniAILead.id)).where(MiniAILead.assistant_id == assistant_id)
    )
    total = int(total_res.scalar() or 0)

    res = await db.execute(
        select(MiniAILead)
        .where(MiniAILead.assistant_id == assistant_id)
        .order_by(MiniAILead.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(res.scalars().all()), total
