# app/modules/knowledge_bases/repositories/knowledge_base_repository.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_base import KnowledgeBase


class KnowledgeBaseRepository:

    async def create(
        self,
        db: AsyncSession,
        knowledge_base: KnowledgeBase
    ):
        db.add(knowledge_base)

        await db.flush()

        await db.refresh(
            knowledge_base
        )

        return knowledge_base

    async def get_by_id(
        self,
        db: AsyncSession,
        knowledge_base_id: int
    ):
        result = await db.execute(
            select(
                KnowledgeBase
            ).where(
                KnowledgeBase.id
                ==
                knowledge_base_id
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
                KnowledgeBase
            ).where(
                KnowledgeBase.code
                ==
                code
            )
        )

        return result.scalar_one_or_none()

    async def list_all(
        self,
        db: AsyncSession
    ):
        result = await db.execute(
            select(
                KnowledgeBase
            )
        )

        return result.scalars().all()
    
    async def update(
        self,
        db: AsyncSession,
        knowledge_base: KnowledgeBase
    ):
        await db.flush()

        await db.refresh(
            knowledge_base
        )

        return knowledge_base
    
    async def list_active(
        self,
        db: AsyncSession
    ):
        result = await db.execute(
            select(
                KnowledgeBase
            ).where(
                KnowledgeBase.is_active.is_(True)
            )
        )

        return result.scalars().all()
    
    async def deactivate(
        self,
        db: AsyncSession,
        knowledge_base: KnowledgeBase
    ):
        knowledge_base.is_active = False

        await db.flush()

        await db.refresh(
            knowledge_base
        )

        return knowledge_base


knowledge_base_repository = (
    KnowledgeBaseRepository()
)