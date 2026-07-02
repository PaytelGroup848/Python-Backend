from sqlalchemy import (
    select
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.workspace_knowledge_bases.models.workspace_knowledge_base import (
    WorkspaceKnowledgeBase
)


class WorkspaceKnowledgeBaseRepository:

    async def create(

        self,

        db: AsyncSession,

        workspace_knowledge_base: WorkspaceKnowledgeBase

    ):

        db.add(
            workspace_knowledge_base
        )

        await db.flush()

        await db.refresh(
            workspace_knowledge_base
        )

        return workspace_knowledge_base

    async def get_by_id(

        self,

        db: AsyncSession,

        workspace_knowledge_base_id: int

    ):

        result = await db.execute(

            select(
                WorkspaceKnowledgeBase
            )
            .where(
                WorkspaceKnowledgeBase.id
                ==
                workspace_knowledge_base_id
            )

        )

        return result.scalar_one_or_none()

    async def list_by_workspace(

        self,

        db: AsyncSession,

        workspace_id: int

    ):

        result = await db.execute(

            select(
                WorkspaceKnowledgeBase
            )
            .where(
                WorkspaceKnowledgeBase.workspace_id
                ==
                workspace_id
            )
            .order_by(
                WorkspaceKnowledgeBase.priority.asc()
            )

        )

        return result.scalars().all()

    async def get_default(

        self,

        db: AsyncSession,

        workspace_id: int

    ):

        result = await db.execute(

            select(
                WorkspaceKnowledgeBase
            )
            .where(
                WorkspaceKnowledgeBase.workspace_id
                ==
                workspace_id,
                WorkspaceKnowledgeBase.is_default
                ==
                True,
                WorkspaceKnowledgeBase.is_active
                ==
                True
            )

        )

        return result.scalar_one_or_none()

    async def deactivate_defaults(

        self,

        db: AsyncSession,

        workspace_id: int

    ):

        result = await db.execute(

            select(
                WorkspaceKnowledgeBase
            )
            .where(
                WorkspaceKnowledgeBase.workspace_id
                ==
                workspace_id,
                WorkspaceKnowledgeBase.is_default
                ==
                True
            )

        )

        records = result.scalars().all()

        for record in records:

            record.is_default = False

        await db.flush()

        return records

    async def update(

        self,

        db: AsyncSession,

        workspace_knowledge_base: WorkspaceKnowledgeBase

    ):

        await db.flush()

        await db.refresh(
            workspace_knowledge_base
        )

        return workspace_knowledge_base


workspace_knowledge_base_repository = (
    WorkspaceKnowledgeBaseRepository()
)