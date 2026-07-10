from copy import (
    deepcopy,
)

from sqlalchemy import (
    select,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.models.model_version import (
    ModelVersion,
)

from app.modules.datasets.repositories.dataset_repository import (
    dataset_repository,
)

from app.modules.datasets.repositories.dataset_snapshot_repository import (
    dataset_snapshot_repository,
)

from app.modules.models.repositories.model_repository import (
    ModelRepository,
)

from app.modules.tokenizers.repositories.tokenizer_training_lifecycle_repository import (
    tokenizer_training_lifecycle_repository,
)

from app.modules.training.models.training_configuration import (
    TrainingConfiguration,
)

from app.modules.training.repositories.training_job_repository import (
    training_job_repository,
)

from app.modules.training_providers.repositories.training_provider_repository import (
    training_provider_repository,
)

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime,
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

        if job is None:
            raise ValueError(
                "Training job not found."
            )

        provider = await (
            training_provider_repository
            .get_by_id(
                db=db,
                provider_id=(
                    job.training_provider_id
                ),
            )
        )

        if provider is None:
            raise ValueError(
                "Training provider not found."
            )

        if not provider.is_active:
            raise ValueError(
                "Training provider is inactive."
            )

        if (
            not provider.runtime_class
            or
            not provider.runtime_class.strip()
        ):
            raise ValueError(
                "Training provider has no "
                "runtime class."
            )

        dataset = await (
            dataset_repository
            .get_by_id(
                db=db,
                dataset_id=job.dataset_id,
            )
        )

        if dataset is None:
            raise ValueError(
                "Dataset not found."
            )

        model = await (
            model_repository
            .get_by_id(
                db=db,
                model_id=job.base_model_id,
            )
        )

        if model is None:
            raise ValueError(
                "Base model not found."
            )

        model_version = await (
            self._load_base_model_version(
                db=db,
                base_model_version_id=(
                    job.base_model_version_id
                ),
                base_model_id=model.id,
            )
        )

        tokenizer_version = await (
            self._load_tokenizer_version(
                db=db,
                tokenizer_version_id=(
                    job.tokenizer_version_id
                ),
            )
        )

        snapshot = await (
            self._load_dataset_snapshot(
                db=db,
                dataset_id=dataset.id,
                dataset_snapshot_id=(
                    job.dataset_snapshot_id
                ),
            )
        )

        training_configuration = await (
            self._load_training_configuration(
                db=db,
                training_configuration_id=(
                    job.training_configuration_id
                ),
                training_type=job.training_type,
            )
        )

        runtime_configuration = (
            self._build_runtime_configuration(
                configuration_json=(
                    training_configuration
                    .configuration_json
                ),
                tokenizer_version=(
                    tokenizer_version
                ),
            )
        )

        return TrainingRuntime(
            training_job_id=job.id,

            dataset_id=dataset.id,

            dataset_snapshot_id=snapshot.id,

            snapshot_record_count=(
                snapshot.record_count
            ),

            snapshot_max_record_id=(
                snapshot.max_record_id
            ),

            snapshot_content_hash=(
                snapshot.content_hash
            ),

            provider_id=provider.id,

            provider_code=provider.code,

            runtime_type=(
                provider.provider_type
            ),

            runtime_code=(
                training_configuration.runtime_code
            ),

            runtime_class=(
                provider.runtime_class
            ),

            runtime_version=(
                provider.runtime_version
            ),

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

            tokenizer_version_id=(
                tokenizer_version.id
            ),

            tokenizer_id=(
                tokenizer_version.tokenizer_id
            ),

            tokenizer_version=(
                tokenizer_version.version
            ),

            tokenizer_content_hash=(
                tokenizer_version.content_hash
            ),

            training_configuration_id=(
                training_configuration.id
            ),

            training_type=(
                job.training_type
            ),

            runtime_configuration=(
                runtime_configuration
            ),

            capabilities=(
                deepcopy(
                    provider.capabilities
                    or
                    {}
                )
            ),

            status=job.status,

            artifact_directory=(
                job.artifact_path
            ),
        )


    async def _load_base_model_version(
        self,
        db: AsyncSession,
        base_model_version_id: int | None,
        base_model_id: int,
    ) -> ModelVersion:

        if base_model_version_id is None:
            raise ValueError(
                "Training job is not bound to "
                "a base model version."
            )

        result = await db.execute(
            select(
                ModelVersion
            )
            .where(
                ModelVersion.id
                ==
                base_model_version_id
            )
        )

        model_version = (
            result.scalar_one_or_none()
        )

        if model_version is None:
            raise ValueError(
                "Base model version not found."
            )

        if (
            model_version.model_id
            !=
            base_model_id
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

        return model_version


    async def _load_tokenizer_version(
        self,
        db: AsyncSession,
        tokenizer_version_id: int | None,
    ):

        if tokenizer_version_id is None:
            raise ValueError(
                "Training job is not bound to "
                "a tokenizer version."
            )

        tokenizer_version = await (
            tokenizer_training_lifecycle_repository
            .get_version_by_id(
                db=db,
                tokenizer_version_id=(
                    tokenizer_version_id
                ),
            )
        )

        if tokenizer_version is None:
            raise ValueError(
                "Tokenizer version not found."
            )

        if not tokenizer_version.is_active:
            raise ValueError(
                "Tokenizer version is inactive."
            )

        if not tokenizer_version.is_immutable:
            raise ValueError(
                "Training requires an immutable "
                "tokenizer version."
            )

        if (
            not tokenizer_version.content_hash
            or
            not tokenizer_version.content_hash.strip()
        ):
            raise ValueError(
                "Tokenizer version has no "
                "content hash."
            )

        return tokenizer_version


    async def _load_dataset_snapshot(
        self,
        db: AsyncSession,
        dataset_id: int,
        dataset_snapshot_id: int | None,
    ):

        if dataset_snapshot_id is None:
            raise ValueError(
                "Training job is not bound to "
                "a dataset snapshot."
            )

        snapshot = await (
            dataset_snapshot_repository
            .get_by_id(
                db=db,
                snapshot_id=(
                    dataset_snapshot_id
                ),
            )
        )

        if snapshot is None:
            raise ValueError(
                "Dataset snapshot not found."
            )

        if snapshot.dataset_id != dataset_id:
            raise ValueError(
                "Dataset snapshot does not belong "
                "to the training dataset."
            )

        if snapshot.status.upper() != "SEALED":
            raise ValueError(
                "Training requires a SEALED "
                "dataset snapshot."
            )

        if not snapshot.is_immutable:
            raise ValueError(
                "Training requires an immutable "
                "dataset snapshot."
            )

        return snapshot


    async def _load_training_configuration(
        self,
        db: AsyncSession,
        training_configuration_id: int,
        training_type: str,
    ) -> TrainingConfiguration:

        result = await db.execute(
            select(
                TrainingConfiguration
            )
            .where(
                TrainingConfiguration.id
                ==
                training_configuration_id
            )
        )

        training_configuration = (
            result.scalar_one_or_none()
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
            training_type
        ):
            raise ValueError(
                "Training configuration type does "
                "not match the training job type."
            )

        return training_configuration


    @staticmethod
    def _build_runtime_configuration(
        configuration_json: dict | None,
        tokenizer_version,
    ) -> dict:

        runtime_configuration = deepcopy(
            configuration_json
            or
            {}
        )

        tokenizer_configuration = (
            runtime_configuration.get(
                "tokenizer"
            )
        )

        if not isinstance(
            tokenizer_configuration,
            dict,
        ):
            raise ValueError(
                "Training configuration must define "
                "'tokenizer' as an object."
            )

        version_metadata = (
            tokenizer_version
            .version_metadata_json
            or
            {}
        )

        if not isinstance(
            version_metadata,
            dict,
        ):
            raise ValueError(
                "Tokenizer version metadata must "
                "be an object."
            )

        version_runtime_configuration = (
            version_metadata.get(
                "runtime_configuration",
                {}
            )
        )

        if not isinstance(
            version_runtime_configuration,
            dict,
        ):
            raise ValueError(
                "Tokenizer version runtime "
                "configuration must be an object."
            )

        prepared_tokenizer_configuration = deepcopy(
            tokenizer_configuration
        )

        algorithm_configuration = (
            prepared_tokenizer_configuration.get(
                "configuration",
                {}
            )
        )

        if not isinstance(
            algorithm_configuration,
            dict,
        ):
            raise ValueError(
                "Tokenizer algorithm configuration "
                "must be an object."
            )

        resolved_algorithm_configuration = deepcopy(
            version_runtime_configuration
        )

        resolved_algorithm_configuration.update(
            algorithm_configuration
        )

        prepared_tokenizer_configuration[
            "configuration"
        ] = resolved_algorithm_configuration

        prepared_tokenizer_configuration[
            "version_lineage"
        ] = {
            "tokenizer_id": (
                tokenizer_version.tokenizer_id
            ),
            "tokenizer_version_id": (
                tokenizer_version.id
            ),
            "tokenizer_version": (
                tokenizer_version.version
            ),
            "content_hash": (
                tokenizer_version.content_hash
            ),
        }

        runtime_configuration[
            "tokenizer"
        ] = prepared_tokenizer_configuration

        return runtime_configuration


training_runtime_service = (
    TrainingRuntimeService()
)