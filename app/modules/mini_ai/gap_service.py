import re
from sqlalchemy import func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.mini_ai.models import MiniAIGap


def normalize_question(question: str) -> str:
    cleaned = re.sub(r"[^\w\s]", " ", question.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


async def record_gap(
    db: AsyncSession,
    assistant_id: int,
    question: str,
) -> None:
    norm = normalize_question(question)
    if not norm:
        return

    # Atomic upsert against partial unique index (assistant_id, md5(normalized_question)) WHERE resolved = false
    upsert_sql = text("""
        INSERT INTO mini_ai_gaps (assistant_id, question, normalized_question, hit_count, resolved, created_at, updated_at)
        VALUES (:assistant_id, :question, :normalized_question, 1, false, NOW(), NOW())
        ON CONFLICT (assistant_id, md5(normalized_question)) WHERE resolved = false
        DO UPDATE SET
            hit_count = mini_ai_gaps.hit_count + 1,
            updated_at = NOW()
    """)
    await db.execute(
        upsert_sql,
        {
            "assistant_id": assistant_id,
            "question": question.strip()[:1000],
            "normalized_question": norm[:1000],
        },
    )


async def list_gaps(
    db: AsyncSession,
    assistant_id: int,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[MiniAIGap], int]:
    total_res = await db.execute(
        select(func.count(MiniAIGap.id)).where(MiniAIGap.assistant_id == assistant_id)
    )
    total = int(total_res.scalar() or 0)

    res = await db.execute(
        select(MiniAIGap)
        .where(MiniAIGap.assistant_id == assistant_id)
        .order_by(MiniAIGap.resolved.asc(), MiniAIGap.hit_count.desc(), MiniAIGap.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(res.scalars().all()), total


async def resolve_gap(
    db: AsyncSession,
    gap_id: int,
    assistant_id: int,
) -> MiniAIGap | None:
    res = await db.execute(
        select(MiniAIGap).where(
            MiniAIGap.id == gap_id,
            MiniAIGap.assistant_id == assistant_id,
        )
    )
    gap = res.scalar_one_or_none()
    if gap is None:
        return None
    await db.execute(
        update(MiniAIGap)
        .where(MiniAIGap.id == gap_id)
        .values(resolved=True)
    )
    gap.resolved = True
    return gap
