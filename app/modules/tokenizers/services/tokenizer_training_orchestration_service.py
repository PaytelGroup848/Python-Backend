import hashlib
import json
import tempfile

from datetime import (
    datetime,
)

from pathlib import (
    Path,
    PurePosixPath,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.tokenizers.models.tokenizer_version import (
    TokenizerVersion,
)

from app.modules.tokenizers.models.tokenizer_version_artifact import (
    TokenizerVersionArtifact,
)

from app.modules.tokenizers.repositories.tokenizer_training_lifecycle_repository import (
    tokenizer_training_lifecycle_repository,
)

from app.modules.tokenizers.services.tokenizer_trainer_resolution_service import (
    tokenizer_trainer_resolution_service,
)

from app.modules.training_runtime.services.training_data_runtime_service import (
    training_data_runtime_service,
)

from app.modules.storage_runtime.services.storage_resolution_service import (
    storage_resolution_service,
)


class TokenizerTrainingOrchestrationService:

    async def execute(
        self,
        db: AsyncSession,
        job_id: int,
        tokenizer_id: int,
        tokenizer_version: str,
        display_name: str,
        storage_instance_id: int,
        object_key_prefix: str,
        organization_id: int | None = None,
        workspace_id: int | None = None,
    ) -> TokenizerVersion:

        if job_id <= 0:
            raise ValueError(
                "job_id must be greater than zero."
            )

        if tokenizer_id <= 0:
            raise ValueError(
                "tokenizer_id must be greater than zero."
            )

        if storage_instance_id <= 0:
            raise ValueError(
                "storage_instance_id must be greater than zero."
            )

        normalized_version = (
            tokenizer_version.strip()
        )

        if not normalized_version:
            raise ValueError(
                "tokenizer_version is required."
            )

        normalized_display_name = (
            display_name.strip()
        )

        if not normalized_display_name:
            raise ValueError(
                "display_name is required."
            )

        normalized_object_key_prefix = (
            object_key_prefix
            .strip()
            .replace("\\", "/")
            .strip("/")
        )

        if not normalized_object_key_prefix:
            raise ValueError(
                "object_key_prefix is required."
            )

        published_references: list[str] = []

        resolved_storage = None

        stream = None

        try:

            job = await (
                tokenizer_training_lifecycle_repository
                .get_job_by_id(
                    db=db,
                    job_id=job_id,
                    for_update=True,
                )
            )

            if job is None:
                raise ValueError(
                    "Tokenizer training job not found."
                )

            configuration = await (
                tokenizer_training_lifecycle_repository
                .get_training_configuration_by_id(
                    db=db,
                    configuration_id=(
                        job.tokenizer_training_configuration_id
                    ),
                )
            )

            if configuration is None:
                raise ValueError(
                    "Tokenizer training configuration "
                    "not found."
                )

            if not configuration.is_active:
                raise ValueError(
                    "Tokenizer training configuration "
                    "is inactive."
                )

            implementation = await (
                tokenizer_training_lifecycle_repository
                .get_implementation_by_id(
                    db=db,
                    implementation_id=(
                        configuration.tokenizer_implementation_id
                    ),
                )
            )

            if implementation is None:
                raise ValueError(
                    "Tokenizer implementation not found."
                )

            if not implementation.is_active:
                raise ValueError(
                    "Tokenizer implementation is inactive."
                )

            trainer = (
                tokenizer_trainer_resolution_service
                .resolve(
                    implementation=implementation,
                )
            )

            configuration_json = (
                configuration.configuration_json
                or
                {}
            )

            if not isinstance(
                configuration_json,
                dict,
            ):
                raise ValueError(
                    "Tokenizer training configuration "
                    "must be an object."
                )

            stream_configuration = (
                configuration_json.get(
                    "stream",
                    {},
                )
            )

            if not isinstance(
                stream_configuration,
                dict,
            ):
                raise ValueError(
                    "Tokenizer stream configuration "
                    "must be an object."
                )

            batch_size = (
                stream_configuration.get(
                    "batch_size"
                )
            )

            if (
                not isinstance(
                    batch_size,
                    int,
                )
                or
                batch_size <= 0
            ):
                raise ValueError(
                    "Tokenizer stream configuration must "
                    "define a positive batch_size."
                )

            trainer_configuration = (
                configuration_json.get(
                    "trainer",
                    {},
                )
            )

            if not isinstance(
                trainer_configuration,
                dict,
            ):
                raise ValueError(
                    "Tokenizer trainer configuration "
                    "must be an object."
                )

            stream = await (
                training_data_runtime_service
                .open_snapshot_stream(
                    db=db,
                    dataset_snapshot_id=(
                        job.dataset_snapshot_id
                    ),
                    batch_size=batch_size,
                )
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

            job.status = "RUNNING"
            job.started_at = (
                job.started_at
                or
                datetime.utcnow()
            )
            job.failure_message = None

            await db.flush()

            with tempfile.TemporaryDirectory(
                prefix=(
                    f"tokenizer-job-{job.id}-"
                )
            ) as temporary_directory:

                output_directory = Path(
                    temporary_directory
                ).resolve()

                result = await trainer.train(
                    training_data=stream,
                    configuration=(
                        trainer_configuration
                    ),
                    output_directory=(
                        output_directory
                    ),
                )

                output_root = (
                    output_directory.resolve()
                )

                for artifact in result.artifacts:

                    artifact_path = (
                        artifact.local_path.resolve()
                    )

                    try:

                        artifact_path.relative_to(
                            output_root
                        )

                    except ValueError as exc:

                        raise ValueError(
                            "Tokenizer trainer artifact "
                            "escapes the temporary output "
                            "directory."
                        ) from exc

                    if not artifact_path.is_file():
                        raise FileNotFoundError(
                            str(
                                artifact_path
                            )
                        )

                manifest_payload = {
                    "training_job_id": job.id,
                    "dataset_snapshot_id": (
                        job.dataset_snapshot_id
                    ),
                    "training_configuration_id": (
                        configuration.id
                    ),
                    "training_configuration_version": (
                        configuration.version
                    ),
                    "implementation_id": (
                        implementation.id
                    ),
                    "implementation_code": (
                        implementation.implementation_code
                    ),
                    "implementation_version": (
                        implementation.implementation_version
                    ),
                    "algorithm_type": (
                        implementation.algorithm_type
                    ),
                    "trainer_class": (
                        implementation.trainer_class
                    ),
                    "tokenizer_class": (
                        implementation.tokenizer_class
                    ),
                    "vocabulary_size": (
                        result.vocabulary_size
                    ),
                    "runtime_configuration": (
                        result.runtime_configuration
                    ),
                    "trainer_metadata": (
                        result.metadata
                    ),
                }

                canonical_manifest = (
                    json.dumps(
                        manifest_payload,
                        sort_keys=True,
                        separators=(
                            ",",
                            ":",
                        ),
                        ensure_ascii=False,
                    )
                    .encode(
                        "utf-8"
                    )
                )

                content_hash = (
                    hashlib.sha256(
                        canonical_manifest
                    )
                    .hexdigest()
                )

                published_artifacts = []

                for artifact in result.artifacts:

                    object_key = str(
                        PurePosixPath(
                            normalized_object_key_prefix
                        )
                        /
                        artifact.artifact_code
                    )

                    storage_object = await (
                        resolved_storage.runtime
                        .publish_file(
                            source_path=(
                                artifact.local_path
                            ),
                            object_key=(
                                object_key
                            ),
                            mime_type=(
                                artifact.mime_type
                            ),
                            metadata={
                                **artifact.metadata,
                                "training_job_id": (
                                    job.id
                                ),
                                "dataset_snapshot_id": (
                                    job.dataset_snapshot_id
                                ),
                                "implementation_id": (
                                    implementation.id
                                ),
                            },
                        )
                    )

                    if (
                        not storage_object.checksum
                    ):
                        raise RuntimeError(
                            "Published tokenizer artifact "
                            "does not have a checksum."
                        )

                    published_references.append(
                        storage_object.storage_reference
                    )

                    published_artifacts.append(
                        (
                            artifact,
                            storage_object,
                        )
                    )

                tokenizer_version_entity = (
                    TokenizerVersion(
                        tokenizer_id=(
                            tokenizer_id
                        ),
                        tokenizer_training_job_id=(
                            job.id
                        ),
                        version=(
                            normalized_version
                        ),
                        display_name=(
                            normalized_display_name
                        ),
                        status="READY",
                        vocabulary_size=(
                            result.vocabulary_size
                        ),
                        content_hash=(
                            content_hash
                        ),
                        version_metadata_json={
                            "dataset_snapshot_id": (
                                job.dataset_snapshot_id
                            ),
                            "training_configuration_id": (
                                configuration.id
                            ),
                            "implementation_id": (
                                implementation.id
                            ),
                            "implementation_code": (
                                implementation.implementation_code
                            ),
                            "implementation_version": (
                                implementation.implementation_version
                            ),
                            "algorithm_type": (
                                implementation.algorithm_type
                            ),
                            "trainer_class": (
                                implementation.trainer_class
                            ),
                            "tokenizer_class": (
                                implementation.tokenizer_class
                            ),
                            "runtime_configuration": (
                                result.runtime_configuration
                            ),
                            "trainer_metadata": (
                                result.metadata
                            ),
                        },
                        is_immutable=True,
                        is_active=True,
                    )
                )

                tokenizer_version_entity = await (
                    tokenizer_training_lifecycle_repository
                    .create_version(
                        db=db,
                        version=(
                            tokenizer_version_entity
                        ),
                    )
                )

                for (
                    artifact,
                    storage_object,
                ) in published_artifacts:

                    await (
                        tokenizer_training_lifecycle_repository
                        .create_version_artifact(
                            db=db,
                            artifact=(
                                TokenizerVersionArtifact(
                                    tokenizer_version_id=(
                                        tokenizer_version_entity.id
                                    ),
                                    storage_instance_id=(
                                        storage_instance_id
                                    ),
                                    artifact_code=(
                                        artifact.artifact_code
                                    ),
                                    artifact_type=(
                                        artifact.artifact_type
                                    ),
                                    storage_reference=(
                                        storage_object.storage_reference
                                    ),
                                    mime_type=(
                                        storage_object.mime_type
                                    ),
                                    size_bytes=(
                                        storage_object.size_bytes
                                    ),
                                    checksum=(
                                        storage_object.checksum
                                    ),
                                    metadata_json={
                                        **artifact.metadata,
                                        **storage_object.metadata,
                                    },
                                )
                            ),
                        )
                    )

                job.status = "COMPLETED"
                job.completed_at = (
                    datetime.utcnow()
                )
                job.failure_message = None

                await db.flush()

                await db.commit()

                return tokenizer_version_entity

        except Exception as exc:

            await db.rollback()

            if (
                resolved_storage is not None
                and
                published_references
            ):

                for storage_reference in reversed(
                    published_references
                ):

                    try:

                        await (
                            resolved_storage.runtime
                            .delete(
                                storage_reference=(
                                    storage_reference
                                )
                            )
                        )

                    except Exception:

                        pass

            try:

                job = await (
                    tokenizer_training_lifecycle_repository
                    .get_job_by_id(
                        db=db,
                        job_id=job_id,
                        for_update=True,
                    )
                )

                if job is not None:

                    job.status = "FAILED"
                    job.failure_message = str(
                        exc
                    )

                    await db.commit()

            except Exception:

                await db.rollback()

            raise

        finally:

            if stream is not None:

                await stream.aclose()


tokenizer_training_orchestration_service = (
    TokenizerTrainingOrchestrationService()
)