from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.models.model_version import (
    ModelVersion,
)

from app.modules.model_artifacts.repositories.model_artifact_repository import (
    model_artifact_repository,
)

from app.modules.models.repositories.model_version_repository import (
    model_version_repository,
)

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime,
)
from app.shared.constants.model_version_status import (
    ModelVersionStatus,
)

class ModelVersionService:

    async def get_by_id(
        self,
        db: AsyncSession,
        model_version_id: int,
    ):

        return await (
            model_version_repository
            .get_by_id(
                db=db,
                model_version_id=model_version_id,
            )
        )
    
    async def list_by_model(
        self,
        db: AsyncSession,
        model_id: int,
    ):

        return await (
            model_version_repository
            .list_by_model(
                db=db,
                model_id=model_id,
            )
        )
    
    async def get_by_training_job(
        self,
        db: AsyncSession,
        training_job_id: int,
    ):

        return await (
            model_version_repository
            .get_by_training_job(
                db=db,
                training_job_id=training_job_id,
            )
        )
    
    async def get_by_artifact(
        self,
        db: AsyncSession,
        artifact_id: int,
    ):

        return await (
            model_version_repository
            .get_by_artifact(
                db=db,
                artifact_id=artifact_id,
            )
        )
    
    async def create_from_training(
        self,
        db: AsyncSession,
        runtime: TrainingRuntime,
        version: str,
        display_name: str,
        description: str | None = None,
        parent_model_version_id: int | None = None,
    ) -> ModelVersion:

        existing_model_version = await (
            model_version_repository
            .get_by_training_job(
                db=db,
                training_job_id=runtime.training_job_id,
            )
        )

        if existing_model_version is not None:

            return existing_model_version

        artifact = await (
            model_artifact_repository
            .get_latest_by_type(
                db=db,
                training_job_id=runtime.training_job_id,
                artifact_type=(
                    runtime.runtime_configuration
                    .get(
                        "final_artifact",
                        {},
                    )
                    .get(
                        "artifact_type"
                    )
                ),
            )
        )

        if artifact is None:

            raise ValueError(
                "Final model artifact "
                "was not found."
            )

        model_version = ModelVersion(

            model_id=runtime.base_model_id,

            training_job_id=runtime.training_job_id,

            artifact_id=artifact.id,

            version=version,

            display_name=display_name,

            description=description,

            status=ModelVersionStatus.CREATED,

            is_active=True,

            is_release_ready=False,

            is_deployment_ready=False,

            source_type=runtime.base_model_source_type,

            source_uri=runtime.base_model_source_uri,

            source_revision=runtime.base_model_source_revision,

            parent_model_version_id=(
                parent_model_version_id
            ),
        )

        return await (
            model_version_repository
            .create(
                db=db,
                model_version=model_version,
            )
        )
    
    async def activate(
        self,
        db: AsyncSession,
        model_version_id: int,
    ) -> ModelVersion:

        model_version = await (
            model_version_repository
            .get_by_id(
                db=db,
                model_version_id=model_version_id,
            )
        )

        if model_version is None:

            raise ValueError(
                "Model version not found."
            )

        model_version.is_active = True

        return await (
            model_version_repository
            .update(
                db=db,
                model_version=model_version,
            )
        )
    
    async def deactivate(
        self,
        db: AsyncSession,
        model_version_id: int,
    ) -> ModelVersion:

        model_version = await (
            model_version_repository
            .get_by_id(
                db=db,
                model_version_id=model_version_id,
            )
        )

        if model_version is None:

            raise ValueError(
                "Model version not found."
            )

        model_version.is_active = False

        return await (
            model_version_repository
            .update(
                db=db,
                model_version=model_version,
            )
        )
    
    async def mark_release_ready(
        self,
        db: AsyncSession,
        model_version_id: int,
    ) -> ModelVersion:

        model_version = await (
            model_version_repository
            .get_by_id(
                db=db,
                model_version_id=model_version_id,
            )
        )

        if model_version is None:

            raise ValueError(
                "Model version not found."
            )

        model_version.is_release_ready = True

        model_version.status = (
            ModelVersionStatus.RELEASE_READY
        )

        return await (
            model_version_repository
            .update(
                db=db,
                model_version=model_version,
            )
        )
    
    async def mark_deployment_ready(
        self,
        db: AsyncSession,
        model_version_id: int,
    ) -> ModelVersion:

        model_version = await (
            model_version_repository
            .get_by_id(
                db=db,
                model_version_id=model_version_id,
            )
        )

        if model_version is None:

            raise ValueError(
                "Model version not found."
            )

        model_version.is_deployment_ready = True

        model_version.status = (
            ModelVersionStatus.DEPLOYMENT_READY
        )

        return await (
            model_version_repository
            .update(
                db=db,
                model_version=model_version,
            )
        )
    
    async def delete(
        self,
        db: AsyncSession,
        model_version_id: int,
    ) -> bool:

        model_version = await (
            model_version_repository
            .get_by_id(
                db=db,
                model_version_id=model_version_id,
            )
        )

        if model_version is None:

            return False

        await (
            model_version_repository
            .delete(
                db=db,
                model_version=model_version,
            )
        )

        return True
    
model_version_service = (
    ModelVersionService()
)