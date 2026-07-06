from fastapi import (
    HTTPException,
    status
)
from app.core.config import (
    settings
)
device = settings.MODEL_DEFAULT_DEVICE

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.model_releases.repositories.model_release_repository import (
    model_release_repository
)

from app.modules.model_artifacts.repositories.model_artifact_repository import (
    model_artifact_repository
)

from app.modules.model_runtime.manager.model_runtime_manager import (
    model_runtime_manager
)

from app.modules.workspace_runtime.schemas.workspace_runtime_schema import (
    WorkspaceRuntime
)

from app.modules.model_releases.services.release_artifact_resolver_service import (
    release_artifact_resolver_service
)


class ModelRuntimeService:

    async def load_runtime(

        self,

        db: AsyncSession,

        workspace_runtime: WorkspaceRuntime

    ):

        release = await (

            model_release_repository
            .get_by_id(

                db=db,

                release_id=workspace_runtime.model_release_id

            )

        )

        if release is None:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Model release not found"

            )

        if not release.is_active:

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail="Model release is inactive"

            )

        artifact = await (
            release_artifact_resolver_service
            .resolve(
                db=db,
                release=release
            )
        )

        if artifact is None:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Artifact not found"

            )

        return await (

            model_runtime_manager
            .load_runtime(

                release_id=release.id,

                artifact_id=artifact.id,

                artifact_path=artifact.artifact_path,

                model_name=release.release_name,

                tokenizer_path=artifact.tokenizer_path,

                device=device

            )

        )

    async def unload_model(

        self,

        release_id: int

    ):

        await (

            model_runtime_manager
            .unload_model(

                release_id

            )

        )

    async def reload_runtime(

        self,

        db: AsyncSession,

        release_id: int

    ):

        await (

            self.unload_model(

                release_id

            )

        )

        return await (

            self.load_runtime(

                db=db,

                release_id=release_id

            )

        )

    def get_runtime(

        self,

        release_id: int

    ):

        return (

            model_runtime_manager

            .get_runtime(

                release_id

            )

        )


model_runtime_service = (
    ModelRuntimeService()
)