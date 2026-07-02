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

from app.modules.workspace_knowledge_bases.schemas.workspace_knowledge_base_create import (
    WorkspaceKnowledgeBaseCreate
)

from app.modules.workspace_knowledge_bases.schemas.workspace_knowledge_base_update import (
    WorkspaceKnowledgeBaseUpdate
)

from app.modules.workspace_knowledge_bases.schemas.workspace_knowledge_base_response import (
    WorkspaceKnowledgeBaseResponse
)

from app.modules.workspace_knowledge_bases.services.workspace_knowledge_base_service import (
    workspace_knowledge_base_service
)


router = APIRouter(

    prefix="/workspace-knowledge-bases",

    tags=["Workspace Knowledge Bases"]

)


@router.post(

    "/",

    response_model=WorkspaceKnowledgeBaseResponse,

    status_code=status.HTTP_201_CREATED

)
async def assign_knowledge_base(

    data: WorkspaceKnowledgeBaseCreate,

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (

        workspace_knowledge_base_service
        .assign_knowledge_base(

            db=db,

            data=data

        )

    )


@router.get(

    "/{workspace_knowledge_base_id}",

    response_model=WorkspaceKnowledgeBaseResponse

)
async def get_workspace_knowledge_base(

    workspace_knowledge_base_id: int,

    db: AsyncSession = Depends(
        get_db
    )

):

    mapping = await (

        workspace_knowledge_base_service
        .get(

            db=db,

            workspace_knowledge_base_id=workspace_knowledge_base_id

        )

    )

    if mapping is None:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Workspace knowledge base not found"

        )

    return mapping


@router.get(

    "/workspace/{workspace_id}",

    response_model=list[WorkspaceKnowledgeBaseResponse]

)
async def list_workspace_knowledge_bases(

    workspace_id: int,

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (

        workspace_knowledge_base_service
        .list_workspace_knowledge_bases(

            db=db,

            workspace_id=workspace_id

        )

    )


@router.patch(

    "/{workspace_knowledge_base_id}",

    response_model=WorkspaceKnowledgeBaseResponse

)
async def update_workspace_knowledge_base(

    workspace_knowledge_base_id: int,

    data: WorkspaceKnowledgeBaseUpdate,

    db: AsyncSession = Depends(
        get_db
    )

):

    mapping = await (

        workspace_knowledge_base_service
        .get(

            db=db,

            workspace_knowledge_base_id=workspace_knowledge_base_id

        )

    )

    if mapping is None:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Workspace knowledge base not found"

        )

    return await (

        workspace_knowledge_base_service
        .update(

            db=db,

            workspace_knowledge_base=mapping,

            data=data

        )

    )