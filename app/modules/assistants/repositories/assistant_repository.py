from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant import Assistant


class AssistantRepository:

    async def create(
        self,
        db: AsyncSession,
        assistant: Assistant
    ):
        db.add(assistant)

        await db.flush()

        await db.refresh(
            assistant
        )

        return assistant

    async def get_by_id(
        self,
        db: AsyncSession,
        assistant_id: int
    ):
        result = await db.execute(
            select(
                Assistant
            ).where(
                Assistant.id
                ==
                assistant_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_code(
        self,
        db: AsyncSession,
        code: str
    ):
        result = await db.execute(
            select(
                Assistant
            ).where(
                Assistant.code
                ==
                code
            )
        )

        return result.scalar_one_or_none()

    async def list_active(
        self,
        db: AsyncSession
    ):
        result = await db.execute(
            select(
                Assistant
            ).where(
                Assistant.is_active == True
            )
        )

        return result.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        assistant: Assistant
    ):
        await db.flush()

        await db.refresh(
            assistant
        )

        return assistant


assistant_repository = (
    AssistantRepository()
)