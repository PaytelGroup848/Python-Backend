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

from app.modules.workspace_assistants.schemas.workspace_assistant_create import (
    WorkspaceAssistantCreate
)

from app.modules.workspace_assistants.schemas.workspace_assistant_update import (
    WorkspaceAssistantUpdate
)

from app.modules.workspace_assistants.schemas.workspace_assistant_response import (
    WorkspaceAssistantResponse
)

from app.modules.workspace_assistants.services.workspace_assistant_service import (
    workspace_assistant_service
)


router = APIRouter(

    prefix="/workspace-assistants",

    tags=["Workspace Assistants"]

)


@router.post(

    "/",

    response_model=WorkspaceAssistantResponse,

    status_code=status.HTTP_201_CREATED

)
async def assign_assistant(

    data: WorkspaceAssistantCreate,

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (
        workspace_assistant_service
        .assign_assistant(
            db=db,
            data=data
        )
    )


@router.get(

    "/{workspace_assistant_id}",

    response_model=WorkspaceAssistantResponse

)
async def get_workspace_assistant(

    workspace_assistant_id: int,

    db: AsyncSession = Depends(
        get_db
    )

):

    workspace_assistant = await (
        workspace_assistant_service
        .get(
            db=db,
            workspace_assistant_id=workspace_assistant_id
        )
    )

    if workspace_assistant is None:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Workspace assistant not found"

        )

    return workspace_assistant


@router.get(

    "/workspace/{workspace_id}",

    response_model=list[WorkspaceAssistantResponse]

)
async def list_workspace_assistants(

    workspace_id: int,

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (
        workspace_assistant_service
        .list_workspace_assistants(
            db=db,
            workspace_id=workspace_id
        )
    )


@router.patch(

    "/{workspace_assistant_id}",

    response_model=WorkspaceAssistantResponse

)
async def update_workspace_assistant(

    workspace_assistant_id: int,

    data: WorkspaceAssistantUpdate,

    db: AsyncSession = Depends(
        get_db
    )

):

    workspace_assistant = await (
        workspace_assistant_service
        .get(
            db=db,
            workspace_assistant_id=workspace_assistant_id
        )
    )

    if workspace_assistant is None:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Workspace assistant not found"

        )

    return await (
        workspace_assistant_service
        .update(
            db=db,
            workspace_assistant=workspace_assistant,
            data=data
        )
    )