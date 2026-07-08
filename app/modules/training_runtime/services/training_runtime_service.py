from sqlalchemy import (
    select,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.training.repositories.training_job_repository import (
    training_job_repository,
)

from app.modules.datasets.repositories.dataset_repository import (
    dataset_repository,
)

from app.modules.datasets.repositories.dataset_snapshot_repository import (
    dataset_snapshot_repository,
)

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime,
)

from app.modules.training_providers.repositories.training_provider_repository import (
    training_provider_repository,
)

from app.modules.models.repositories.model_repository import (
    ModelRepository,
)

from app.modules.training.models.training_configuration import (
    TrainingConfiguration,
)

from app.models.model_version import (
    ModelVersion,
)
model_repository = (
    ModelRepository()
)

class TrainingRuntimeService:

    async def load_runtime(
        self,
        db: AsyncSession,
        training_job_id: int,
    ) -> TrainingRuntime:

        job = await (
            training_job_repository
            .get_by_id(
                db=db,
                training_job_id=training_job_id,
            )
        )

        if not job:
            raise ValueError(
                "Training job not found"
            )

        provider = await (
            training_provider_repository
            .get_by_id(
                db=db,
                provider_id=job.training_provider_id,
            )
        )

        if not provider:
            raise ValueError(
                "Training provider not found"
            )

        if not provider.is_active:
            raise ValueError(
                "Training provider is inactive"
            )

        dataset = await (
            dataset_repository
            .get_by_id(
                db=db,
                dataset_id=job.dataset_id,
            )
        )

        if not dataset:
            raise ValueError(
                "Dataset not found"
            )

        model = await (
            model_repository
            .get_by_id(
                db=db,
                model_id=job.base_model_id,
            )
        )

        if not model:
            raise ValueError(
                "Base model not found"
            )
        
        if job.base_model_version_id is None:
            raise ValueError(
                "Training job is not bound to "
                "a base model version."
            )

        model_version_result = await db.execute(
            select(
                ModelVersion
            )
            .where(
                ModelVersion.id
                ==
                job.base_model_version_id
            )
        )

        model_version = (
            model_version_result
            .scalar_one_or_none()
        )

        if model_version is None:
            raise ValueError(
                "Base model version not found."
            )

        if (
            model_version.model_id
            !=
            model.id
        ):
            raise ValueError(
                "Base model version does not belong "
                "to the training base model."
            )

        if not model_version.is_active:
            raise ValueError(
                "Base model version is inactive."
            )

        if (
            not model_version.source_type
            or
            not model_version.source_type.strip()
        ):
            raise ValueError(
                "Base model version has no "
                "source type."
            )

        if (
            not model_version.source_uri
            or
            not model_version.source_uri.strip()
        ):
            raise ValueError(
                "Base model version has no "
                "source URI."
            )

        if job.dataset_snapshot_id is None:
            raise ValueError(
                "Training job is not bound to a dataset snapshot."
            )

        snapshot = await (
            dataset_snapshot_repository
            .get_by_id(
                db=db,
                snapshot_id=job.dataset_snapshot_id,
            )
        )

        if snapshot is None:
            raise ValueError(
                "Dataset snapshot not found."
            )

        if snapshot.dataset_id != dataset.id:
            raise ValueError(
                "Dataset snapshot does not belong "
                "to the training dataset."
            )

        if snapshot.status.upper() != "SEALED":
            raise ValueError(
                "Training requires a SEALED dataset snapshot."
            )

        if not snapshot.is_immutable:
            raise ValueError(
                "Training requires an immutable dataset snapshot."
            )

        configuration_result = await db.execute(
            select(
                TrainingConfiguration
            )
            .where(
                TrainingConfiguration.id
                ==
                job.training_configuration_id
            )
        )

        training_configuration = (
            configuration_result
            .scalar_one_or_none()
        )

        if training_configuration is None:
            raise ValueError(
                "Training configuration not found."
            )

        if not training_configuration.is_active:
            raise ValueError(
                "Training configuration is inactive."
            )

        if (
            training_configuration.training_type
            !=
            job.training_type
        ):
            raise ValueError(
                "Training configuration type does not match "
                "the training job type."
            )

        if (
            training_configuration.runtime_code.upper()
            !=
            provider.runtime_code.upper()
        ):
            raise ValueError(
                "Training configuration runtime does not match "
                "the selected training provider runtime."
            )

        return TrainingRuntime(
            training_job_id=job.id,

            dataset_id=dataset.id,

            dataset_snapshot_id=snapshot.id,

            snapshot_record_count=snapshot.record_count,

            snapshot_max_record_id=snapshot.max_record_id,

            snapshot_content_hash=snapshot.content_hash,

            provider_id=provider.id,

            provider_code=provider.code,

            runtime_type=provider.runtime_type,

            runtime_code=provider.runtime_code,

            runtime_class=(
                provider.runtime_class
            ),

            runtime_version=provider.runtime_version,

            base_model_id=model.id,

            base_model_code=model.code,

            base_model_version_id=(
                model_version.id
            ),

            base_model_version=(
                model_version.version
            ),

            base_model_source_type=(
                model_version.source_type
            ),

            base_model_source_uri=(
                model_version.source_uri
            ),

            base_model_source_revision=(
                model_version.source_revision
            ),

            training_configuration_id=(
                training_configuration.id
            ),

            training_type=job.training_type,

            runtime_configuration=(
                training_configuration.configuration_json
                or
                {}
            ),

            capabilities=(
                provider.capabilities
                or
                {}
            ),

            status=job.status,

            artifact_directory=job.artifact_path,
        )


training_runtime_service = (
    TrainingRuntimeService()
)