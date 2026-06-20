from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant_knowledge_base import (
    AssistantKnowledgeBase
)


class AssistantKnowledgeBaseRepository:

    async def create(
        self,
        db: AsyncSession,
        mapping: AssistantKnowledgeBase
    ):
        db.add(mapping)

        await db.flush()

        await db.refresh(
            mapping
        )

        return mapping

    async def get_mapping(
        self,
        db: AsyncSession,
        assistant_id: int,
        knowledge_base_id: int
    ):
        result = await db.execute(
            select(
                AssistantKnowledgeBase
            ).where(
                AssistantKnowledgeBase.assistant_id
                ==
                assistant_id,

                AssistantKnowledgeBase.knowledge_base_id
                ==
                knowledge_base_id,

                AssistantKnowledgeBase.is_active
                ==
                True
            )
        )

        return result.scalar_one_or_none()

    async def list_by_assistant(
        self,
        db: AsyncSession,
        assistant_id: int
    ):
        result = await db.execute(
            select(
                AssistantKnowledgeBase
            ).where(
                AssistantKnowledgeBase.assistant_id
                ==
                assistant_id,

                AssistantKnowledgeBase.is_active
                ==
                True
            )
        )

        return result.scalars().all()

    async def list_by_knowledge_base(
        self,
        db: AsyncSession,
        knowledge_base_id: int
    ):
        result = await db.execute(
            select(
                AssistantKnowledgeBase
            ).where(
                AssistantKnowledgeBase.knowledge_base_id
                ==
                knowledge_base_id,

                AssistantKnowledgeBase.is_active
                ==
                True
            )
        )

        return result.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        mapping: AssistantKnowledgeBase
    ):
        await db.flush()

        await db.refresh(
            mapping
        )

        return mapping


assistant_knowledge_base_repository = (
    AssistantKnowledgeBaseRepository()
)