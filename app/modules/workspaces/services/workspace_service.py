from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from fastapi import (
    HTTPException,
    status
)

from app.shared.context.request_context import (
    RequestContext
)

from app.modules.organizations.repositories.organization_repository import (
    organization_repository
)

from app.modules.workspaces.models.workspace import (
    Workspace
)

from app.modules.workspaces.repositories.workspace_repository import (
    workspace_repository
)

from app.modules.workspaces.schemas.workspace_create import (
    WorkspaceCreate
)

from app.modules.workspaces.schemas.workspace_update import (
    WorkspaceUpdate
)


class WorkspaceService:

    async def create_workspace(

        self,

        db: AsyncSession,

        context: RequestContext,

        data: WorkspaceCreate

    ):

        organization = await (
            organization_repository
            .get_by_id(
                db=db,
                organization_id=context.organization.id
            )
        )

        if not organization:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        existing_code = await (
            workspace_repository
            .get_by_code(
                db=db,
                organization_id=context.organization.id,
                code=data.code
            )
        )

        if existing_code:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Workspace code already exists"
            )

        existing_slug = await (
            workspace_repository
            .get_by_slug(
                db=db,
                organization_id=context.organization.id,
                slug=data.slug
            )
        )

        if existing_slug:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Workspace slug already exists"
            )

        workspace = Workspace(

            organization_id=context.organization.id,

            code=data.code,

            name=data.name,

            slug=data.slug,

            description=data.description,

            icon_url=data.icon_url,

            created_by_user_id=context.user.id

        )

        workspace = await (
            workspace_repository
            .create(
                db=db,
                workspace=workspace
            )
        )

        await db.commit()

        await db.refresh(
            workspace
        )

        return workspace

    async def get_workspace(

        self,

        db: AsyncSession,

        workspace_id: int

    ):

        return await (
            workspace_repository
            .get_by_id(
                db=db,
                workspace_id=workspace_id
            )
        )

    async def list_by_organization(

        self,

        db: AsyncSession,

        organization_id: int

    ):

        return await (
            workspace_repository
            .list_by_organization(
                db=db,
                organization_id=organization_id
            )
        )

    async def update_workspace(

        self,

        db: AsyncSession,

        workspace: Workspace,

        data: WorkspaceUpdate

    ):

        update_data = data.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():

            setattr(
                workspace,
                key,
                value
            )

        workspace = await (
            workspace_repository
            .update(
                db=db,
                workspace=workspace
            )
        )

        await db.commit()

        await db.refresh(
            workspace
        )

        return workspace


workspace_service = (
    WorkspaceService()
)