from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import (
    get_db
)

from app.modules.workspace_models.schemas.workspace_model_create import (
    WorkspaceModelCreate
)

from app.modules.workspace_models.schemas.workspace_model_update import (
    WorkspaceModelUpdate
)

from app.modules.workspace_models.schemas.workspace_model_response import (
    WorkspaceModelResponse
)

from app.modules.workspace_models.services.workspace_model_service import (
    workspace_model_service
)


router = APIRouter(

    prefix="/workspace-models",

    tags=["Workspace Models"]

)


@router.post(

    "/",

    response_model=WorkspaceModelResponse,

    status_code=status.HTTP_201_CREATED

)
async def assign_model(

    data: WorkspaceModelCreate,

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (

        workspace_model_service
        .assign_model(

            db=db,

            data=data

        )

    )


@router.get(

    "/{workspace_model_id}",

    response_model=WorkspaceModelResponse

)
async def get_workspace_model(

    workspace_model_id: int,

    db: AsyncSession = Depends(
        get_db
    )

):

    workspace_model = await (

        workspace_model_service
        .get(

            db=db,

            workspace_model_id=workspace_model_id

        )

    )

    if workspace_model is None:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Workspace model not found"

        )

    return workspace_model


@router.get(

    "/workspace/{workspace_id}",

    response_model=list[WorkspaceModelResponse]

)
async def list_workspace_models(

    workspace_id: int,

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (

        workspace_model_service
        .list_workspace_models(

            db=db,

            workspace_id=workspace_id

        )

    )

@router.get(

    "/workspace/{workspace_id}/default",

    response_model=WorkspaceModelResponse

)
async def get_default_workspace_model(

    workspace_id: int,

    db: AsyncSession = Depends(
        get_db
    )

):

    workspace_model = await (

        workspace_model_service
        .get_default_model(

            db=db,

            workspace_id=workspace_id

        )

    )

    if workspace_model is None:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Default workspace model not found"

        )

    return workspace_model


@router.patch(

    "/{workspace_model_id}",

    response_model=WorkspaceModelResponse

)
async def update_workspace_model(

    workspace_model_id: int,

    data: WorkspaceModelUpdate,

    db: AsyncSession = Depends(
        get_db
    )

):

    workspace_model = await (

        workspace_model_service
        .get(

            db=db,

            workspace_model_id=workspace_model_id

        )

    )

    if workspace_model is None:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Workspace model not found"

        )

    return await (

        workspace_model_service
        .update(

            db=db,

            workspace_model=workspace_model,

            data=data

        )

    )