from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.workspaces.repositories.workspace_repository import (
    workspace_repository
)

from app.modules.assistants.repositories.assistant_repository import (
    assistant_repository
)

from app.modules.workspace_assistants.models.workspace_assistant import (
    WorkspaceAssistant
)

from app.modules.workspace_assistants.repositories.workspace_assistant_repository import (
    workspace_assistant_repository
)

from app.modules.workspace_assistants.schemas.workspace_assistant_create import (
    WorkspaceAssistantCreate
)

from app.modules.workspace_assistants.schemas.workspace_assistant_update import (
    WorkspaceAssistantUpdate
)


class WorkspaceAssistantService:

    async def assign_assistant(

        self,

        db: AsyncSession,

        data: WorkspaceAssistantCreate

    ):

        workspace = await (
            workspace_repository
            .get_by_id(
                db=db,
                workspace_id=data.workspace_id
            )
        )

        if not workspace:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )

        assistant = await (
            assistant_repository
            .get_by_id(
                db=db,
                assistant_id=data.assistant_id
            )
        )

        if not assistant:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assistant not found"
            )

        if data.is_default:

            await (
                workspace_assistant_repository
                .deactivate_defaults(
                    db=db,
                    workspace_id=data.workspace_id
                )
            )

        workspace_assistant = WorkspaceAssistant(

            workspace_id=data.workspace_id,

            assistant_id=data.assistant_id,

            priority=data.priority,

            is_default=data.is_default,

            is_active=data.is_active

        )

        workspace_assistant = await (
            workspace_assistant_repository
            .create(
                db=db,
                workspace_assistant=workspace_assistant
            )
        )

        await db.commit()

        await db.refresh(
            workspace_assistant
        )

        return workspace_assistant

    async def get(

        self,

        db: AsyncSession,

        workspace_assistant_id: int

    ):

        return await (
            workspace_assistant_repository
            .get_by_id(
                db=db,
                workspace_assistant_id=workspace_assistant_id
            )
        )

    async def list_workspace_assistants(

        self,

        db: AsyncSession,

        workspace_id: int

    ):

        return await (
            workspace_assistant_repository
            .list_by_workspace(
                db=db,
                workspace_id=workspace_id
            )
        )

    async def get_default_assistant(

        self,

        db: AsyncSession,

        workspace_id: int

    ):

        return await (
            workspace_assistant_repository
            .get_default(
                db=db,
                workspace_id=workspace_id
            )
        )

    async def update(

        self,

        db: AsyncSession,

        workspace_assistant: WorkspaceAssistant,

        data: WorkspaceAssistantUpdate

    ):

        update_data = data.model_dump(
            exclude_unset=True
        )

        if update_data.get(
            "is_default"
        ):

            await (
                workspace_assistant_repository
                .deactivate_defaults(
                    db=db,
                    workspace_id=workspace_assistant.workspace_id
                )
            )

        for key, value in update_data.items():

            setattr(
                workspace_assistant,
                key,
                value
            )

        workspace_assistant = await (
            workspace_assistant_repository
            .update(
                db=db,
                workspace_assistant=workspace_assistant
            )
        )

        await db.commit()

        await db.refresh(
            workspace_assistant
        )

        return workspace_assistant


workspace_assistant_service = (
    WorkspaceAssistantService()
)