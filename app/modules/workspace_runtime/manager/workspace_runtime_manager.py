from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.workspace_runtime.services.workspace_runtime_service import (
    workspace_runtime_service,
)

from app.modules.workspace_runtime.schemas.workspace_runtime_schema import (
    WorkspaceRuntime,
)


class WorkspaceRuntimeManager:

    async def resolve_runtime(

        self,

        db: AsyncSession,

        workspace_id: int,

    ) -> WorkspaceRuntime:

        return await workspace_runtime_service.load_runtime(

            db=db,

            workspace_id=workspace_id,

        )


workspace_runtime_manager = WorkspaceRuntimeManager()