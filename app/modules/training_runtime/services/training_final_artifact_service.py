import io

import torch

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.model_artifacts.models.model_artifact import (
    ModelArtifact,
)

from app.modules.model_artifacts.repositories.model_artifact_repository import (
    model_artifact_repository,
)

from app.modules.storage_runtime.services.storage_resolution_service import (
    storage_resolution_service,
)

from app.modules.training_runtime.contracts.trainable_model import (
    TrainableModel,
)

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime,
)


class TrainingFinalArtifactService:

    

    async def publish(
        self,
        db: AsyncSession,
        runtime: TrainingRuntime,
        model: TrainableModel,
        strategy_metadata: dict,
        configuration: dict,
        organization_id: int | None = None,
        workspace_id: int | None = None,
    ) -> ModelArtifact:

        if not isinstance(
            strategy_metadata,
            dict,
        ):
            raise ValueError(
                "Strategy metadata must be an object."
            )

        if not isinstance(
            configuration,
            dict,
        ):
            raise ValueError(
                "Final artifact configuration "
                "must be an object."
            )

        storage_configuration = (
            configuration.get(
                "storage"
            )
        )

        if not isinstance(
            storage_configuration,
            dict,
        ):
            raise ValueError(
                "Final artifact configuration must "
                "define 'storage' as an object."
            )

        storage_instance_id = (
            storage_configuration.get(
                "storage_instance_id"
            )
        )

        if (
            isinstance(
                storage_instance_id,
                bool,
            )
            or
            not isinstance(
                storage_instance_id,
                int,
            )
            or
            storage_instance_id <= 0
        ):
            raise ValueError(
                "Final artifact storage must define "
                "a positive integer "
                "'storage_instance_id'."
            )

        object_key_template = (
            configuration.get(
                "object_key_template"
            )
        )

        if (
            not isinstance(
                object_key_template,
                str,
            )
            or
            not object_key_template.strip()
        ):
            raise ValueError(
                "Final artifact configuration must "
                "define 'object_key_template'."
            )

        artifact_type = (
            configuration.get(
                "artifact_type"
            )
        )

        if (
            not isinstance(
                artifact_type,
                str,
            )
            or
            not artifact_type.strip()
        ):
            raise ValueError(
                "Final artifact configuration must "
                "define 'artifact_type'."
            )

        artifact_name_template = (
            configuration.get(
                "artifact_name_template"
            )
        )

        if (
            not isinstance(
                artifact_name_template,
                str,
            )
            or
            not artifact_name_template.strip()
        ):
            raise ValueError(
                "Final artifact configuration must "
                "define 'artifact_name_template'."
            )
        
        format_version = (
            configuration.get(
                "format_version"
            )
        )

        if (
            isinstance(
                format_version,
                bool,
            )
            or
            not isinstance(
                format_version,
                int,
            )
            or
            format_version <= 0
        ):
            raise ValueError(
                "Final artifact configuration must "
                "define a positive integer "
                "'format_version'."
            )

        object_key = (
            object_key_template.format(
                training_job_id=(
                    runtime.training_job_id
                ),
                dataset_snapshot_id=(
                    runtime.dataset_snapshot_id
                ),
                base_model_version_id=(
                    runtime.base_model_version_id
                ),
                tokenizer_version_id=(
                    runtime.tokenizer_version_id
                ),
                training_configuration_id=(
                    runtime.training_configuration_id
                ),
            )
        )

        artifact_name = (
            artifact_name_template.format(
                training_job_id=(
                    runtime.training_job_id
                ),
                dataset_snapshot_id=(
                    runtime.dataset_snapshot_id
                ),
                base_model_version_id=(
                    runtime.base_model_version_id
                ),
                tokenizer_version_id=(
                    runtime.tokenizer_version_id
                ),
                training_configuration_id=(
                    runtime.training_configuration_id
                ),
            )
        )

        if not object_key.strip():
            raise ValueError(
                "Resolved final artifact object key "
                "is empty."
            )

        if not artifact_name.strip():
            raise ValueError(
                "Resolved final artifact name "
                "is empty."
            )

        resolved_storage = await (
            storage_resolution_service
            .resolve(
                db=db,
                storage_instance_id=(
                    storage_instance_id
                ),
                organization_id=(
                    organization_id
                ),
                workspace_id=(
                    workspace_id
                ),
            )
        )

        payload = {
            "format_version": (
                format_version
            ),
            "lineage": {
                "training_job_id": (
                    runtime.training_job_id
                ),
                "dataset_id": (
                    runtime.dataset_id
                ),
                "dataset_snapshot_id": (
                    runtime.dataset_snapshot_id
                ),
                "snapshot_content_hash": (
                    runtime.snapshot_content_hash
                ),
                "base_model_id": (
                    runtime.base_model_id
                ),
                "base_model_version_id": (
                    runtime.base_model_version_id
                ),
                "base_model_source_type": (
                    runtime.base_model_source_type
                ),
                "base_model_source_uri": (
                    runtime.base_model_source_uri
                ),
                "base_model_source_revision": (
                    runtime.base_model_source_revision
                ),
                "tokenizer_version_id": (
                    runtime.tokenizer_version_id
                ),
                "tokenizer_content_hash": (
                    runtime.tokenizer_content_hash
                ),
                "training_configuration_id": (
                    runtime.training_configuration_id
                ),
                "training_type": (
                    runtime.training_type
                ),
                "runtime_code": (
                    runtime.runtime_code
                ),
                "runtime_version": (
                    runtime.runtime_version
                ),
            },
            "model_state_dict": (
                model.state_dict()
            ),
            "strategy_metadata": dict(
                strategy_metadata
            ),

            "artifact_metadata": {
                "artifact_type": artifact_type.strip(),
                "format_version": format_version,
            },
        }

        buffer = io.BytesIO()

        torch.save(
            payload,
            buffer,
        )

        artifact_bytes = (
            buffer.getvalue()
        )

        if not artifact_bytes:
            raise ValueError(
                "Final training artifact payload "
                "is empty."
            )

        storage_object = await (
            resolved_storage.runtime
            .publish_bytes(
                content=artifact_bytes,
                object_key=(
                    object_key.strip()
                ),
                mime_type=(
                    "application/octet-stream"
                ),
                metadata={
                    "format_version": (
                        format_version
                    ),
                    "artifact_type": (
                        artifact_type.strip()
                    ),
                    "training_job_id": (
                        runtime.training_job_id
                    ),
                    "dataset_snapshot_id": (
                        runtime.dataset_snapshot_id
                    ),
                    "base_model_version_id": (
                        runtime.base_model_version_id
                    ),
                    "tokenizer_version_id": (
                        runtime.tokenizer_version_id
                    ),
                    "training_configuration_id": (
                        runtime.training_configuration_id
                    ),
                },
            )
        )

        if (
            not storage_object.storage_reference
            or
            not storage_object.storage_reference.strip()
        ):
            raise ValueError(
                "Storage runtime returned no "
                "storage reference."
            )

        artifact = ModelArtifact(
            training_job_id=(
                runtime.training_job_id
            ),
            artifact_name=(
                artifact_name.strip()
            ),
            artifact_path=None,
            artifact_type=(
                artifact_type.strip()
            ),
            artifact_version=(
                format_version
            ),
            storage_provider=(
                storage_object.storage_provider
            ),
            storage_instance_id=(
                resolved_storage
                .storage_instance_id
            ),
            storage_reference=(
                storage_object
                .storage_reference
            ),
            metadata_json={
                "format_version": (
                    format_version
                ),
                "lineage": (
                    payload["lineage"]
                ),

                "model_version_reference": {
                    "id": None,
                    "version": None,
                },
                "strategy_metadata": dict(
                    strategy_metadata
                ),
                "storage_metadata": dict(
                    storage_object.metadata
                ),
            },
            mime_type=(
                storage_object.mime_type
            ),
            compression=None,
            status="READY",
            size_bytes=(
                storage_object.size_bytes
            ),
            checksum=(
                storage_object.checksum
            ),
        )

        artifact = await (
            model_artifact_repository
            .create(
                db=db,
                artifact=artifact,
            )
        )

        

        return artifact


training_final_artifact_service = (
    TrainingFinalArtifactService()
)