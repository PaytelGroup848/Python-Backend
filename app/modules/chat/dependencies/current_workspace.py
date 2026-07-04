from fastapi import (
    Depends,
    HTTPException,
    Path,
    status,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.database import (
    get_db,
)

from app.shared.context.request_context import (
    RequestContext,
)

from app.modules.auth.dependencies.current_request_context import (
    get_request_context,
)

from app.modules.workspaces.models.workspace import (
    Workspace,
)

from app.modules.workspaces.services.workspace_service import (
    workspace_service,
)


async def get_current_workspace(

    workspace_id: int = Path(...),

    context: RequestContext = Depends(
        get_request_context
    ),

    db: AsyncSession = Depends(
        get_db
    ),

) -> Workspace:

    workspace = await workspace_service.get_workspace(

        db=db,

        workspace_id=workspace_id,

    )

    if workspace is None:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Workspace not found",

        )

    if workspace.organization_id != context.organization.id:

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="Workspace does not belong to your organization",

        )

    return workspace