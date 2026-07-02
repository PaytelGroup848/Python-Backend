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

from app.modules.knowledge_bases.repositories.knowledge_base_repository import (
    knowledge_base_repository
)

from app.modules.workspace_knowledge_bases.models.workspace_knowledge_base import (
    WorkspaceKnowledgeBase
)

from app.modules.workspace_knowledge_bases.repositories.workspace_knowledge_base_repository import (
    workspace_knowledge_base_repository
)

from app.modules.workspace_knowledge_bases.schemas.workspace_knowledge_base_create import (
    WorkspaceKnowledgeBaseCreate
)

from app.modules.workspace_knowledge_bases.schemas.workspace_knowledge_base_update import (
    WorkspaceKnowledgeBaseUpdate
)


class WorkspaceKnowledgeBaseService:

    async def assign_knowledge_base(

        self,

        db: AsyncSession,

        data: WorkspaceKnowledgeBaseCreate

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

        knowledge_base = await (
            knowledge_base_repository
            .get_by_id(
                db=db,
                knowledge_base_id=data.knowledge_base_id
            )
        )

        if not knowledge_base:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge base not found"
            )

        if data.is_default:

            await (
                workspace_knowledge_base_repository
                .deactivate_defaults(
                    db=db,
                    workspace_id=data.workspace_id
                )
            )

        mapping = WorkspaceKnowledgeBase(

            workspace_id=data.workspace_id,

            knowledge_base_id=data.knowledge_base_id,

            priority=data.priority,

            is_default=data.is_default,

            is_active=data.is_active

        )

        mapping = await (
            workspace_knowledge_base_repository
            .create(
                db=db,
                workspace_knowledge_base=mapping
            )
        )

        await db.commit()

        await db.refresh(
            mapping
        )

        return mapping

    async def get(

        self,

        db: AsyncSession,

        workspace_knowledge_base_id: int

    ):

        return await (
            workspace_knowledge_base_repository
            .get_by_id(
                db=db,
                workspace_knowledge_base_id=workspace_knowledge_base_id
            )
        )

    async def list_workspace_knowledge_bases(

        self,

        db: AsyncSession,

        workspace_id: int

    ):

        return await (
            workspace_knowledge_base_repository
            .list_by_workspace(
                db=db,
                workspace_id=workspace_id
            )
        )

    async def update(

        self,

        db: AsyncSession,

        workspace_knowledge_base: WorkspaceKnowledgeBase,

        data: WorkspaceKnowledgeBaseUpdate

    ):

        update_data = data.model_dump(
            exclude_unset=True
        )

        if update_data.get(
            "is_default"
        ):

            await (
                workspace_knowledge_base_repository
                .deactivate_defaults(
                    db=db,
                    workspace_id=workspace_knowledge_base.workspace_id
                )
            )

        for key, value in update_data.items():

            setattr(
                workspace_knowledge_base,
                key,
                value
            )

        workspace_knowledge_base = await (
            workspace_knowledge_base_repository
            .update(
                db=db,
                workspace_knowledge_base=workspace_knowledge_base
            )
        )

        await db.commit()

        await db.refresh(
            workspace_knowledge_base
        )

        return workspace_knowledge_base


workspace_knowledge_base_service = (
    WorkspaceKnowledgeBaseService()
)