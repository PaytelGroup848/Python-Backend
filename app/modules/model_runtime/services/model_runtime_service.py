from fastapi import (
    HTTPException,
    status
)

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


class ModelRuntimeService:

    async def load_model(

        self,

        db: AsyncSession,

        release_id: int

    ):

        release = await (

            model_release_repository
            .get_by_id(

                db=db,

                release_id=release_id

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

            model_artifact_repository
            .get_by_id(

                db=db,

                artifact_id=release.artifact_id

            )

        )

        if artifact is None:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Artifact not found"

            )

        return await (

            model_runtime_manager
            .load_model(

                release_id=release.id,

                artifact_id=artifact.id,

                artifact_path=artifact.artifact_path,

                model_name=release.name,

                tokenizer_path=artifact.tokenizer_path,

                device="cuda"

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

    async def reload_model(

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

            self.load_model(

                db=db,

                release_id=release_id

            )

        )

    def get_loaded_model(

        self,

        release_id: int

    ):

        return (

            model_runtime_manager
            .get_loaded_model(

                release_id

            )

        )


model_runtime_service = (
    ModelRuntimeService()
)