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

from app.modules.model_releases.repositories.model_release_repository import (
    model_release_repository
)

from app.modules.workspace_models.models.workspace_model import (
    WorkspaceModel
)

from app.modules.workspace_models.repositories.workspace_model_repository import (
    workspace_model_repository
)

from app.modules.workspace_models.schemas.workspace_model_create import (
    WorkspaceModelCreate
)

from app.modules.workspace_models.schemas.workspace_model_update import (
    WorkspaceModelUpdate
)


class WorkspaceModelService:

    async def assign_model(

        self,

        db: AsyncSession,

        data: WorkspaceModelCreate

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

        model_release = await (
            model_release_repository
            .get_by_id(
                db=db,
                release_id=data.model_release_id
            )
        )

        if not model_release:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Model release not found"

            )

        if not model_release.is_active:

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail="Model release is inactive"

            )

        if data.is_default:

            await (
                workspace_model_repository
                .deactivate_defaults(
                    db=db,
                    workspace_id=data.workspace_id
                )
            )

        workspace_model = WorkspaceModel(

            workspace_id=data.workspace_id,

            model_release_id=data.model_release_id,

            priority=data.priority,

            is_default=data.is_default,

            is_active=data.is_active

        )

        workspace_model = await (
            workspace_model_repository
            .create(
                db=db,
                workspace_model=workspace_model
            )
        )

        await db.commit()

        await db.refresh(
            workspace_model
        )

        return workspace_model

    async def get(

        self,

        db: AsyncSession,

        workspace_model_id: int

    ):

        return await (
            workspace_model_repository
            .get_by_id(
                db=db,
                workspace_model_id=workspace_model_id
            )
        )

    async def list_workspace_models(

        self,

        db: AsyncSession,

        workspace_id: int

    ):

        return await (
            workspace_model_repository
            .list_by_workspace(
                db=db,
                workspace_id=workspace_id
            )
        )

    async def get_default_model(

        self,

        db: AsyncSession,

        workspace_id: int

    ):

        return await (
            workspace_model_repository
            .get_default(
                db=db,
                workspace_id=workspace_id
            )
        )

    async def update(

        self,

        db: AsyncSession,

        workspace_model: WorkspaceModel,

        data: WorkspaceModelUpdate

    ):

        update_data = data.model_dump(
            exclude_unset=True
        )

        if update_data.get(
            "is_default"
        ):

            await (
                workspace_model_repository
                .deactivate_defaults(
                    db=db,
                    workspace_id=workspace_model.workspace_id
                )
            )

        for key, value in update_data.items():

            setattr(
                workspace_model,
                key,
                value
            )

        workspace_model = await (
            workspace_model_repository
            .update(
                db=db,
                workspace_model=workspace_model
            )
        )

        await db.commit()

        await db.refresh(
            workspace_model
        )

        return workspace_model


workspace_model_service = (
    WorkspaceModelService()
)