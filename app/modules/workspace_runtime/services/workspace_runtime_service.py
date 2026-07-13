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

from app.modules.workspace_models.repositories.workspace_model_repository import (
    workspace_model_repository
)

from app.modules.workspace_knowledge_bases.repositories.workspace_knowledge_base_repository import (
    workspace_knowledge_base_repository
)

from app.modules.workspace_assistants.repositories.workspace_assistant_repository import (
    workspace_assistant_repository
)

from app.modules.model_releases.repositories.model_release_repository import (
    model_release_repository
)

from app.modules.assistants.repositories.assistant_repository import (
    assistant_repository
)

from app.modules.workspace_runtime.schemas.workspace_runtime_schema import (
    WorkspaceRuntime
)

from app.modules.models.repositories.model_deployment_repository import (
    model_deployment_repository,
)

from app.modules.models.repositories.model_version_repository import (
    model_version_repository,
)

class WorkspaceRuntimeService:

    async def load_runtime(

        self,

        db: AsyncSession,

        workspace_id: int

    ) -> WorkspaceRuntime:

        workspace = await (
            workspace_repository
            .get_by_id(
                db=db,
                workspace_id=workspace_id
            )
        )

        if workspace is None:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Workspace not found"

            )

        workspace_model = await (
            workspace_model_repository
            .get_default(
                db=db,
                workspace_id=workspace.id
            )
        )

        if workspace_model is None:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Workspace model not configured"

            )

        model_release = await (
            model_release_repository
            .get_by_id(
                db=db,
                release_id=workspace_model.model_release_id
            )
        )

        if model_release is None:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Model release not found"

            )
        
        model_version = await (

            model_version_repository

            .get_by_id(

                db=db,

                model_version_id=model_release.model_version_id,

            )

        )

        if model_version is None:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Model version not found",

            )
        
        deployment = await (

            model_deployment_repository

            .get_by_model_version(

                db=db,

                model_version_id=model_version.id,

            )

        )

        if deployment is None:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Model deployment not found",

            )

        workspace_assistant = await (
            workspace_assistant_repository
            .get_default(
                db=db,
                workspace_id=workspace.id
            )
        )

        assistant_id: int | None = None

        if workspace_assistant:

            assistant = await (
                assistant_repository
                .get_by_id(
                    db=db,
                    assistant_id=workspace_assistant.assistant_id
                )
            )

            if assistant:

                assistant_id = assistant.id

        workspace_kbs = await (
            workspace_knowledge_base_repository
            .list_by_workspace(
                db=db,
                workspace_id=workspace.id
            )
        )

        knowledge_base_ids = [

            kb.knowledge_base_id

            for kb in workspace_kbs

            if kb.is_active

        ]

        #
        # TODO:
        # Load workspace tools
        #
        tool_ids: list[int] = []

        #
        # TODO:
        # Resolve workspace system prompt
        #
        system_prompt: str | None = None

        return WorkspaceRuntime(

            workspace_id=
                workspace.id,

            workspace_name=
                workspace.name,

            workspace_slug=
                workspace.slug,

            model_release_id=
                model_release.id,

            model_version_id=
                model_version.id,

            deployment_id=
                deployment.id,

            deployment_name=
                deployment.deployment_name,

            deployment_type=
                deployment.deployment_type,

            assistant_id=
                assistant_id,

            knowledge_base_ids=
                knowledge_base_ids,

            tool_ids=
                tool_ids,

            system_prompt=
                system_prompt,

        )


workspace_runtime_service = (
    WorkspaceRuntimeService()
)