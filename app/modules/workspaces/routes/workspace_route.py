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

from app.shared.context.request_context import (
    RequestContext
)

from app.modules.auth.dependencies.current_request_context import (
    get_request_context
)

from app.modules.workspaces.schemas.workspace_create import (
    WorkspaceCreate
)

from app.modules.workspaces.schemas.workspace_update import (
    WorkspaceUpdate
)

from app.modules.workspaces.schemas.workspace_response import (
    WorkspaceResponse
)

from app.modules.workspaces.services.workspace_service import (
    workspace_service
)


router = APIRouter(

    prefix="/workspaces",

    tags=["Workspaces"]

)


@router.post(

    "/",

    response_model=WorkspaceResponse,

    status_code=status.HTTP_201_CREATED

)
async def create_workspace(

    data: WorkspaceCreate,

    context: RequestContext = Depends(
        get_request_context
    ),

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (

        workspace_service
        .create_workspace(

            db=db,

            context=context,

            data=data

        )

    )


@router.get(

    "/",

    response_model=list[WorkspaceResponse]

)
async def list_workspaces(

    context: RequestContext = Depends(
        get_request_context
    ),

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (

        workspace_service
        .list_by_organization(

            db=db,

            organization_id=context.organization.id

        )

    )


@router.get(

    "/{workspace_id}",

    response_model=WorkspaceResponse

)
async def get_workspace(

    workspace_id: int,

    context: RequestContext = Depends(
        get_request_context
    ),

    db: AsyncSession = Depends(
        get_db
    )

):

    workspace = await (

        workspace_service
        .get_workspace(

            db=db,

            workspace_id=workspace_id

        )

    )

    if workspace is None:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Workspace not found"

        )

    if workspace.organization_id != context.organization.id:

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="Workspace does not belong to your organization"

        )

    return workspace


@router.patch(

    "/{workspace_id}",

    response_model=WorkspaceResponse

)
async def update_workspace(

    workspace_id: int,

    data: WorkspaceUpdate,

    context: RequestContext = Depends(
        get_request_context
    ),

    db: AsyncSession = Depends(
        get_db
    )

):

    workspace = await (

        workspace_service
        .get_workspace(

            db=db,

            workspace_id=workspace_id

        )

    )

    if workspace is None:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Workspace not found"

        )

    if workspace.organization_id != context.organization.id:

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="Workspace does not belong to your organization"

        )

    return await (

        workspace_service
        .update_workspace(

            db=db,

            workspace=workspace,

            data=data

        )

    )


@router.get(

    "/current",

    response_model=WorkspaceResponse

)
async def get_current_workspace(

    context: RequestContext = Depends(
        get_request_context
    )

):

    if context.workspace is None:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="No active workspace selected."

        )

    return context.workspace


@router.post(

    "/{workspace_id}/activate",

    response_model=WorkspaceResponse

)
async def activate_workspace(

    workspace_id: int,

    context: RequestContext = Depends(
        get_request_context
    ),

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (

        workspace_service
        .activate_workspace(

            db=db,

            context=context,

            workspace_id=workspace_id

        )

    )


@router.get(

    "/available",

    response_model=list[WorkspaceResponse]

)
async def available_workspaces(

    context: RequestContext = Depends(
        get_request_context
    ),

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (

        workspace_service
        .list_available_workspaces(

            db=db,

            context=context

        )

    )