from sqlalchemy import (
    select
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.workspace_models.models.workspace_model import (
    WorkspaceModel
)


class WorkspaceModelRepository:

    async def create(

        self,

        db: AsyncSession,

        workspace_model: WorkspaceModel

    ):

        db.add(
            workspace_model
        )

        await db.flush()

        await db.refresh(
            workspace_model
        )

        return workspace_model

    async def get_by_id(

        self,

        db: AsyncSession,

        workspace_model_id: int

    ):

        result = await db.execute(

            select(
                WorkspaceModel
            )
            .where(
                WorkspaceModel.id
                ==
                workspace_model_id
            )

        )

        return result.scalar_one_or_none()

    async def get_default(

        self,

        db: AsyncSession,

        workspace_id: int

    ):

        result = await db.execute(

            select(
                WorkspaceModel
            )
            .where(
                WorkspaceModel.workspace_id
                ==
                workspace_id,
                WorkspaceModel.is_default
                ==
                True,
                WorkspaceModel.is_active
                ==
                True
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
                WorkspaceModel
            )
            .where(
                WorkspaceModel.workspace_id
                ==
                workspace_id
            )

        )

        return result.scalars().all()

    async def get_by_release(

        self,

        db: AsyncSession,

        model_release_id: int

    ):

        result = await db.execute(

            select(
                WorkspaceModel
            )
            .where(
                WorkspaceModel.model_release_id
                ==
                model_release_id
            )

        )

        return result.scalars().all()

    async def update(

        self,

        db: AsyncSession,

        workspace_model: WorkspaceModel

    ):

        await db.flush()

        await db.refresh(
            workspace_model
        )

        return workspace_model

    async def deactivate_defaults(

        self,

        db: AsyncSession,

        workspace_id: int

    ):

        result = await db.execute(

            select(
                WorkspaceModel
            )
            .where(
                WorkspaceModel.workspace_id
                ==
                workspace_id,
                WorkspaceModel.is_default
                ==
                True
            )

        )

        records = result.scalars().all()

        for record in records:

            record.is_default = False

        await db.flush()

        return records


workspace_model_repository = (
    WorkspaceModelRepository()
)