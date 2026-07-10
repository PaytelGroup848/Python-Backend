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

from app.modules.training_runtime.services.training_checkpoint_state_service import (
    training_checkpoint_state_service,
)


class TrainingCheckpointService:

    ARTIFACT_TYPE = "TRAINING_CHECKPOINT"

    async def publish(
        self,
        db: AsyncSession,
        runtime: TrainingRuntime,
        model: TrainableModel,
        strategy_state: dict,
        data_cursor: dict,
        configuration: dict,
        organization_id: int | None = None,
        workspace_id: int | None = None,
    ) -> ModelArtifact:

        if not isinstance(
            configuration,
            dict,
        ):
            raise ValueError(
                "Checkpoint configuration must "
                "be an object."
            )

        if not isinstance(
            strategy_state,
            dict,
        ):
            raise ValueError(
                "Strategy state must be an object."
            )

        if not isinstance(
            data_cursor,
            dict,
        ):
            raise ValueError(
                "Data cursor must be an object."
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
                "Checkpoint configuration must define "
                "'storage' as an object."
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
                "Checkpoint storage must define "
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
                "Checkpoint configuration must define "
                "'object_key_template'."
            )

        step_count = (
            strategy_state.get(
                "step_count",
                0,
            )
        )

        if (
            isinstance(
                step_count,
                bool,
            )
            or
            not isinstance(
                step_count,
                int,
            )
            or
            step_count < 0
        ):
            raise ValueError(
                "Checkpoint strategy step count "
                "is invalid."
            )

        object_key = (
            object_key_template.format(
                training_job_id=(
                    runtime.training_job_id
                ),
                step_count=step_count,
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
                "Resolved checkpoint object key "
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

        payload = (
            training_checkpoint_state_service
            .serialize(
                runtime=runtime,
                model=model,
                strategy_state=(
                    strategy_state
                ),
                data_cursor=(
                    data_cursor
                ),
            )
        )

        if not payload:
            raise ValueError(
                "Checkpoint payload is empty."
            )

        storage_object = await (
            resolved_storage.runtime
            .publish_bytes(
                content=payload,
                object_key=(
                    object_key.strip()
                ),
                mime_type=(
                    "application/octet-stream"
                ),
                metadata={
                    "format_version": 1,
                    "artifact_type": (
                        self.ARTIFACT_TYPE
                    ),
                    "training_job_id": (
                        runtime.training_job_id
                    ),
                    "step_count": (
                        step_count
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
                "checkpoint storage reference."
            )

        artifact = ModelArtifact(
            training_job_id=(
                runtime.training_job_id
            ),
            artifact_name=(
                f"checkpoint-step-{step_count}"
            ),
            artifact_path=None,
            artifact_type=(
                self.ARTIFACT_TYPE
            ),
            artifact_version=1,
            storage_provider=(
                storage_object.storage_provider
            ),
            storage_instance_id=(
                resolved_storage
                .storage_instance_id
            ),
            storage_reference=(
                storage_object.storage_reference
            ),
            metadata_json={
                "format_version": 1,
                "step_count": (
                    step_count
                ),
                "micro_step_count": int(
                    strategy_state.get(
                        "micro_step_count",
                        0,
                    )
                ),
                "data_cursor": dict(
                    data_cursor
                ),
                "dataset_snapshot_id": (
                    runtime.dataset_snapshot_id
                ),
                "snapshot_content_hash": (
                    runtime.snapshot_content_hash
                ),
                "base_model_version_id": (
                    runtime.base_model_version_id
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

        return await (
            model_artifact_repository
            .create(
                db=db,
                artifact=artifact,
            )
        )


    async def restore_latest(
        self,
        db: AsyncSession,
        runtime: TrainingRuntime,
        model: TrainableModel,
        strategy_state: dict,
        organization_id: int | None = None,
        workspace_id: int | None = None,
    ) -> dict | None:

        artifacts = await (
            model_artifact_repository
            .get_by_type(
                db=db,
                training_job_id=(
                    runtime.training_job_id
                ),
                artifact_type=(
                    self.ARTIFACT_TYPE
                ),
            )
        )

        if not artifacts:
            return None

        artifact = artifacts[0]

        if (
            artifact.storage_instance_id is None
            or
            not artifact.storage_reference
            or
            not artifact.storage_reference.strip()
        ):
            raise ValueError(
                "Latest checkpoint has no "
                "storage-native lineage."
            )

        resolved_storage = await (
            storage_resolution_service
            .resolve(
                db=db,
                storage_instance_id=(
                    artifact.storage_instance_id
                ),
                organization_id=(
                    organization_id
                ),
                workspace_id=(
                    workspace_id
                ),
            )
        )

        exists = await (
            resolved_storage.runtime
            .exists(
                storage_reference=(
                    artifact.storage_reference
                )
            )
        )

        if not exists:
            raise ValueError(
                "Checkpoint storage object "
                "does not exist."
            )

        stream = await (
            resolved_storage.runtime
            .open_read(
                storage_reference=(
                    artifact.storage_reference
                )
            )
        )

        try:
            payload = stream.read()

            if hasattr(
                payload,
                "__await__",
            ):
                payload = await payload

        finally:
            close_method = getattr(
                stream,
                "close",
                None,
            )

            if callable(
                close_method
            ):
                close_result = (
                    close_method()
                )

                if hasattr(
                    close_result,
                    "__await__",
                ):
                    await close_result

        if not isinstance(
            payload,
            (bytes, bytearray),
        ):
            raise ValueError(
                "Checkpoint storage payload "
                "is not binary."
            )

        restored = (
            training_checkpoint_state_service
            .restore(
                payload_bytes=bytes(
                    payload
                ),
                runtime=runtime,
                model=model,
                strategy_state=(
                    strategy_state
                ),
            )
        )

        return {
            **restored,
            "artifact_id": (
                artifact.id
            ),
            "storage_instance_id": (
                artifact.storage_instance_id
            ),
            "storage_reference": (
                artifact.storage_reference
            ),
        }


training_checkpoint_service = (
    TrainingCheckpointService()
)