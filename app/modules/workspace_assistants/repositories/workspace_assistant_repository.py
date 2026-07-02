from sqlalchemy import (
    select
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.workspace_assistants.models.workspace_assistant import (
    WorkspaceAssistant
)


class WorkspaceAssistantRepository:

    async def create(

        self,

        db: AsyncSession,

        workspace_assistant: WorkspaceAssistant

    ):

        db.add(
            workspace_assistant
        )

        await db.flush()

        await db.refresh(
            workspace_assistant
        )

        return workspace_assistant

    async def get_by_id(

        self,

        db: AsyncSession,

        workspace_assistant_id: int

    ):

        result = await db.execute(

            select(
                WorkspaceAssistant
            ).where(
                WorkspaceAssistant.id
                ==
                workspace_assistant_id
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
                WorkspaceAssistant
            )
            .where(
                WorkspaceAssistant.workspace_id
                ==
                workspace_id
            )
            .order_by(
                WorkspaceAssistant.priority.asc()
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
                WorkspaceAssistant
            )
            .where(
                WorkspaceAssistant.workspace_id
                ==
                workspace_id,
                WorkspaceAssistant.is_default
                ==
                True,
                WorkspaceAssistant.is_active
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
                WorkspaceAssistant
            )
            .where(
                WorkspaceAssistant.workspace_id
                ==
                workspace_id,
                WorkspaceAssistant.is_default
                ==
                True
            )

        )

        assistants = result.scalars().all()

        for assistant in assistants:

            assistant.is_default = False

        await db.flush()

        return assistants

    async def update(

        self,

        db: AsyncSession,

        workspace_assistant: WorkspaceAssistant

    ):

        await db.flush()

        await db.refresh(
            workspace_assistant
        )

        return workspace_assistant


workspace_assistant_repository = (
    WorkspaceAssistantRepository()
)