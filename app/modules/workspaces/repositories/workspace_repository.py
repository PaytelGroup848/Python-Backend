from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.workspaces.models.workspace import (
    Workspace
)


class WorkspaceRepository:

    async def create(

        self,

        db: AsyncSession,

        workspace: Workspace

    ):

        db.add(
            workspace
        )

        await db.flush()

        await db.refresh(
            workspace
        )

        return workspace

    async def get_by_id(

        self,

        db: AsyncSession,

        workspace_id: int

    ):

        result = await db.execute(

            select(
                Workspace
            )
            .where(
                Workspace.id
                ==
                workspace_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_code(

        self,

        db: AsyncSession,

        organization_id: int,

        code: str

    ):

        result = await db.execute(

            select(
                Workspace
            )
            .where(
                Workspace.organization_id
                ==
                organization_id
            )
            .where(
                Workspace.code
                ==
                code
            )
        )

        return result.scalar_one_or_none()

    async def get_by_slug(

        self,

        db: AsyncSession,

        organization_id: int,

        slug: str

    ):

        result = await db.execute(

            select(
                Workspace
            )
            .where(
                Workspace.organization_id
                ==
                organization_id
            )
            .where(
                Workspace.slug
                ==
                slug
            )
        )

        return result.scalar_one_or_none()

    async def list_by_organization(

        self,

        db: AsyncSession,

        organization_id: int

    ):

        result = await db.execute(

            select(
                Workspace
            )
            .where(
                Workspace.organization_id
                ==
                organization_id
            )
        )

        return result.scalars().all()

    async def update(

        self,

        db: AsyncSession,

        workspace: Workspace

    ):

        await db.flush()

        await db.refresh(
            workspace
        )

        return workspace


workspace_repository = (
    WorkspaceRepository()
)