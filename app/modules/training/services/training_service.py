from sqlalchemy import (
    select,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.models.model import (
    ModelRegistry,
)

from app.modules.training.models.training_job import (
    TrainingJob,
)

from app.modules.training.models.training_configuration import (
    TrainingConfiguration,
)

from app.modules.training.repositories.training_job_repository import (
    training_job_repository,
)

from app.modules.training.schemas.training_job_create import (
    TrainingJobCreate,
)

from app.modules.datasets.repositories.dataset_snapshot_repository import (
    dataset_snapshot_repository,
)

from app.modules.training_providers.models.training_provider import (
    TrainingProvider,
)

from app.shared.exceptions.business_exception import (
    BusinessException,
)

from app.models.model_version import (
    ModelVersion,
)


class TrainingService:

    async def create_training_job(
        self,
        db: AsyncSession,
        data: TrainingJobCreate,
    ):

        snapshot = await (
            dataset_snapshot_repository
            .get_by_id_for_update(
                db,
                data.dataset_snapshot_id,
            )
        )

        if snapshot is None:

            raise BusinessException(
                "Dataset snapshot not found."
            )

        if (
            snapshot.dataset_id
            !=
            data.dataset_id
        ):

            raise BusinessException(
                "Dataset snapshot does not belong "
                "to the requested dataset."
            )

        if snapshot.status.upper() != "SEALED":

            raise BusinessException(
                "Training requires a SEALED "
                "dataset snapshot."
            )

        if not snapshot.is_immutable:

            raise BusinessException(
                "Training requires an immutable "
                "dataset snapshot."
            )

        configuration_result = await db.execute(
            select(
                TrainingConfiguration
            )
            .where(
                TrainingConfiguration.id
                ==
                data.training_configuration_id
            )
        )

        configuration = (
            configuration_result
            .scalar_one_or_none()
        )

        if configuration is None:

            raise BusinessException(
                "Training configuration not found."
            )

        if not configuration.is_active:

            raise BusinessException(
                "Training configuration is inactive."
            )

        if (
            configuration.training_type.upper()
            !=
            data.training_type.upper()
        ):

            raise BusinessException(
                "Training type does not match "
                "the selected configuration."
            )

        provider_result = await db.execute(
            select(
                TrainingProvider
            )
            .where(
                TrainingProvider.id
                ==
                data.training_provider_id
            )
        )

        provider = (
            provider_result
            .scalar_one_or_none()
        )

        if provider is None:

            raise BusinessException(
                "Training provider not found."
            )

        if not provider.is_active:

            raise BusinessException(
                "Training provider is inactive."
            )

        model_result = await db.execute(
            select(
                ModelRegistry
            )
            .where(
                ModelRegistry.id
                ==
                data.base_model_id
            )
        )

        base_model = (
            model_result
            .scalar_one_or_none()
        )

        if base_model is None:

            raise BusinessException(
                "Base model not found."
            )
        
        model_version_result = await db.execute(
            select(
                ModelVersion
            )
            .where(
                ModelVersion.id
                ==
                data.base_model_version_id
            )
        )

        base_model_version = (
            model_version_result
            .scalar_one_or_none()
        )

        if base_model_version is None:

            raise BusinessException(
                "Base model version not found."
            )

        if (
            base_model_version.model_id
            !=
            data.base_model_id
        ):

            raise BusinessException(
                "Base model version does not belong "
                "to the selected base model."
            )

        if not base_model_version.is_active:

            raise BusinessException(
                "Base model version is inactive."
            )

        if (
            not base_model_version.source_type
            or
            not base_model_version.source_uri
        ):

            raise BusinessException(
                "Base model version has no "
                "loadable source configuration."
            )

        training_job = TrainingJob(
            dataset_id=data.dataset_id,
            dataset_snapshot_id=(
                data.dataset_snapshot_id
            ),
            training_provider_id=(
                data.training_provider_id
            ),
            base_model_id=(
                data.base_model_id
            ),
            base_model_version_id=(
                data.base_model_version_id
            ),
            training_configuration_id=(
                data.training_configuration_id
            ),
            training_type=data.training_type,
            priority=data.priority,
            created_by=data.created_by,
            status="PENDING",
        )

        training_job = await (
            training_job_repository
            .create(
                db=db,
                training_job=training_job,
            )
        )

        await db.commit()

        return training_job


    async def get_training_job(
        self,
        db: AsyncSession,
        training_job_id: int,
    ):

        return await (
            training_job_repository
            .get_by_id(
                db,
                training_job_id
            )
        )


    async def list_training_jobs(
        self,
        db: AsyncSession,
    ):

        return await (
            training_job_repository
            .list_all(
                db=db
            )
        )


    async def list_training_jobs_by_status(
        self,
        db: AsyncSession,
        status: str,
    ):

        return await (
            training_job_repository
            .list_by_status(
                db=db,
                status=status
            )
        )


    async def list_training_jobs_by_dataset(
        self,
        db: AsyncSession,
        dataset_id: int,
    ):

        return await (
            training_job_repository
            .list_by_dataset(
                db=db,
                dataset_id=dataset_id
            )
        )


    async def list_training_jobs_by_model(
        self,
        db: AsyncSession,
        base_model_id: int,
    ):

        return await (
            training_job_repository
            .list_by_base_model(
                db=db,
                base_model_id=base_model_id
            )
        )


    async def update_training_job(
        self,
        db: AsyncSession,
        training_job: TrainingJob,
    ):

        training_job = await (
            training_job_repository
            .update(
                db=db,
                training_job=training_job
            )
        )

        await db.commit()

        return training_job


    async def delete_training_job(
        self,
        db: AsyncSession,
        training_job_id: int,
    ) -> bool:

        training_job = await (
            training_job_repository
            .get_by_id(
                db=db,
                training_job_id=training_job_id
            )
        )

        if training_job is None:

            return False

        await (
            training_job_repository
            .delete(
                db=db,
                training_job=training_job
            )
        )

        await db.commit()

        return True


training_service = (
    TrainingService()
)